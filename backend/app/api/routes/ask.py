from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.sql_safety import is_safe_select, references_only_tenant_tables
from app.core.logging_config import get_logger
from app.db.session import get_db
from app.models.ingested_table import IngestedTable
from app.services.conversation import get_or_create_conversation, get_recent_history, save_message
from app.services.embedding import embed_query
from app.services.nl_to_sql import generate_sql
from app.services.query_executor import execute_readonly_query
from app.services.query_router import classify_question
from app.services.rag_answer import generate_answer
from app.services.schema_context import build_schema_context
from app.services.sql_safety import is_safe_select
from app.services.vector_store import search_chunks
from app.schemas.ask import AskRequest, AskResponse
from app.core.auth_dependency import get_current_tenant_id

router = APIRouter(prefix="/ask", tags=["ask"])
logger = get_logger(__name__)


@router.post("", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_tenant_id)):
    conversation = get_or_create_conversation(db, request.conversation_id, tenant_id)
    history = get_recent_history(db, conversation.id)

    save_message(db, conversation.id, "user", request.question)

    has_tables = db.query(IngestedTable).filter(IngestedTable.tenant_id == tenant_id).first() is not None
    has_documents = _has_indexed_documents(tenant_id)

    if has_tables and not has_documents:
        route = "sql"
    elif has_documents and not has_tables:
        route = "document"
    elif has_tables and has_documents:
        from app.services.conversation import get_last_route
        previous_route = get_last_route(db, conversation.id)
        route = classify_question(request.question, previous_route=previous_route)
    else:
        answer = "No data has been uploaded yet. Please upload a document or spreadsheet first."
        save_message(db, conversation.id, "assistant", answer, route="none")
        return AskResponse(question=request.question, route="none", answer=answer, conversation_id=conversation.id)

    logger.info(f"ask_routed question={request.question!r} route={route} conversation_id={conversation.id}")

    if route == "sql":
        result = _handle_sql(request.question, db, tenant_id)
    else:
        result = _handle_document(request.question, history, tenant_id)

    save_message(db, conversation.id, "assistant", result.answer, route=result.route)
    result.conversation_id = conversation.id
    return result


def _has_indexed_documents(tenant_id: str) -> bool:
    from app.db.qdrant_client import qdrant
    from app.services.vector_store import COLLECTION_NAME
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        return False

    count_result = qdrant.count(
        collection_name=COLLECTION_NAME,
        count_filter=Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]),
    )
    return count_result.count > 0


def _handle_sql(question: str, db: Session, tenant_id: str) -> AskResponse:
    tenant_tables = db.query(IngestedTable).filter(IngestedTable.tenant_id == tenant_id).all()
    allowed_table_names = [t.table_name for t in tenant_tables]

    schema_context = build_schema_context(db, tenant_id)
    sql = generate_sql(question, schema_context)

    if "UNSUPPORTED_QUERY" in sql or not is_safe_select(sql):
        return AskResponse(question=question, route="sql", answer="I couldn't answer that using the available data.", conversation_id="")

    if not references_only_tenant_tables(sql, allowed_table_names):
        logger.error(f"cross_tenant_sql_blocked tenant_id={tenant_id} sql={sql!r}")
        return AskResponse(question=question, route="sql", answer="I couldn't answer that using the available data.", conversation_id="")

    try:
        rows, total_count = execute_readonly_query(sql)
        return AskResponse(
            question=question, route="sql", answer=f"Found {total_count} result(s).",
            data=rows, generated_sql=sql, conversation_id="",
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"ask_sql_failed sql={sql!r} error={e}")
        return AskResponse(question=question, route="sql", answer="Query execution failed. Please rephrase your question.", conversation_id="")


def _handle_document(question: str, history: list[dict], tenant_id: str) -> AskResponse:
    query_embedding = embed_query(question)
    results = search_chunks(query_embedding=query_embedding, tenant_id=tenant_id, top_k=5)
    answer = generate_answer(question, results, history=history)
    return AskResponse(question=question, route="document", answer=answer, sources=results, conversation_id="")
