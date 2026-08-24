import json

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.auth_dependency import get_current_tenant_id
from app.core.logging_config import get_logger
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.models.ingested_table import IngestedTable
from app.schemas.ask import AskRequest, AskResponse
from app.services.conversation import get_or_create_conversation, get_recent_history,save_message
from app.services.embedding import embed_query
from app.services.nl_to_sql import generate_sql
from app.services.query_cache import store_query
from app.services.query_executor import execute_readonly_query
from app.services.query_router import classify_question
from app.services.rag_answer import generate_answer
from app.services.schema_context import build_schema_context
from app.services.sql_safety import is_safe_select,references_only_tenant_tables
from app.services.vector_store import search_chunks

router = APIRouter(prefix="/ask", tags=["ask"])
logger = get_logger(__name__)

_FILE_WORDS = (
    "file", "files", "document", "documents", "upload", "uploads",
)

_LIST_WORDS = (
    "show", "list", "what", "which", "give", "display", "all",
)

_VAGUE_FOLLOW_UPS = {
    "more",
    "more information",
    "more info",
    "tell me more",
    "more details",
    "details",
}

_NO_ANSWER_PHRASES = (
    "i couldn't find enough information in the uploaded documents",
    "i couldn't answer that using the available data",
    "query execution failed",
    "no data has been uploaded yet",
)


@router.post("", response_model=AskResponse)
@limiter.limit("10/minute")
def ask(
    request: Request,
    body: AskRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    conversation = get_or_create_conversation(
        db,
        body.conversation_id,
        tenant_id,
    )

    history = get_recent_history(db, conversation.id)

    save_message(db, conversation.id, "user", body.question)

    # Filenames are stored in PostgreSQL, not in Qdrant chunks.
    # Never ask RAG to guess them.
    if _is_file_listing_request(body.question):
        result = _handle_file_listing(body.question, db, tenant_id)

        save_message(
            db,
            conversation.id,
            "assistant",
            result.answer,
            route=result.route,
        )

        result.conversation_id = conversation.id
        return result

    # A vague follow-up has no safe standalone retrieval target.
    if _is_vague_follow_up(body.question):
        answer = (
            "Please specify what topic or document you want more "
            "information about."
        )

        save_message(
            db,
            conversation.id,
            "assistant",
            answer,
            route="document",
        )

        return AskResponse(
            question=body.question,
            route="document",
            answer=answer,
            conversation_id=conversation.id,
        )

    has_tables = (
        db.query(IngestedTable)
        .filter(IngestedTable.tenant_id == tenant_id)
        .first()
        is not None
    )

    has_documents = _has_indexed_documents(tenant_id)

    if has_tables and not has_documents:
        route = "sql"

    elif has_documents and not has_tables:
        route = "document"

    elif has_tables and has_documents:
        from app.services.conversation import get_last_route

        previous_route = get_last_route(db, conversation.id)

        route = classify_question(
            body.question,
            previous_route=previous_route,
        )

    else:
        answer = (
            "No data has been uploaded yet. Please upload a document "
            "or spreadsheet first."
        )

        save_message(
            db,
            conversation.id,
            "assistant",
            answer,
            route="none",
        )

        return AskResponse(
            question=body.question,
            route="none",
            answer=answer,
            conversation_id=conversation.id,
        )

    logger.info(
        "ask_routed question=%r route=%s conversation_id=%s",
        body.question,
        route,
        conversation.id,
    )

    result = _run_route(route, body.question, db, tenant_id, history)

    if (
        _looks_like_no_answer(result.answer)
        and has_tables
        and has_documents
    ):
        fallback_route = "document" if route == "sql" else "sql"
        logger.info(
            "ask_route_fallback original=%s fallback=%s question=%r",
            route,
            fallback_route,
            body.question,
        )
        fallback_result = _run_route(
            fallback_route, body.question, db, tenant_id, history
        )
        if not _looks_like_no_answer(fallback_result.answer):
            result = fallback_result

    message_data = json.dumps(result.data) if result.data else None

    save_message(
        db,
        conversation.id,
        "assistant",
        result.answer,
        route=result.route,
        data=message_data,
        query_id=result.query_id,
    )

    result.conversation_id = conversation.id
    return result


def _run_route(
    route: str,
    question: str,
    db: Session,
    tenant_id: str,
    history: list[dict],
) -> AskResponse:
    if route == "sql":
        return _handle_sql(question, db, tenant_id, history)
    return _handle_document(question, history, tenant_id)


def _looks_like_no_answer(answer: str) -> bool:
    lowered = answer.lower()
    return any(phrase in lowered for phrase in _NO_ANSWER_PHRASES)


def _is_file_listing_request(question: str) -> bool:
    lowered = question.lower()

    return (
        any(word in lowered for word in _FILE_WORDS)
        and any(word in lowered for word in _LIST_WORDS)
    )


def _is_vague_follow_up(question: str) -> bool:
    normalized = " ".join(
        question.lower().strip().rstrip("?!.").split()
    )

    return normalized in _VAGUE_FOLLOW_UPS


def _handle_file_listing(
    question: str,
    db: Session,
    tenant_id: str,
) -> AskResponse:
    documents = (
        db.query(Document)
        .filter(
            Document.tenant_id == tenant_id,
            Document.status == DocumentStatus.READY,
        )
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    if not documents:
        answer = (
            "I couldn't find any ready documents or spreadsheets "
            "for your account."
        )
    else:
        filenames = "\n".join(
            f"- {document.filename}"
            for document in documents
        )
        answer = f"Here are the files currently available:\n{filenames}"

    return AskResponse(
        question=question,
        route="document",
        answer=answer,
        conversation_id="",
    )


def _has_indexed_documents(tenant_id: str) -> bool:
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    from app.db.qdrant_client import qdrant
    from app.services.vector_store import COLLECTION_NAME

    existing = [
        collection.name
        for collection in qdrant.get_collections().collections
    ]

    if COLLECTION_NAME not in existing:
        return False

    count_result = qdrant.count(
        collection_name=COLLECTION_NAME,
        count_filter=Filter(
            must=[
                FieldCondition(
                    key="tenant_id",
                    match=MatchValue(value=tenant_id),
                )
            ]
        ),
    )

    return count_result.count > 0


def _handle_sql(
    question: str,
    db: Session,
    tenant_id: str,
    history: list[dict],
) -> AskResponse:
    tenant_tables = (
        db.query(IngestedTable)
        .filter(IngestedTable.tenant_id == tenant_id)
        .all()
    )

    allowed_table_names = [
        table.table_name
        for table in tenant_tables
    ]

    schema_context = build_schema_context(db, tenant_id)

    sql = generate_sql(
        question,
        schema_context,
        history,
    )

    if "UNSUPPORTED_QUERY" in sql or not is_safe_select(sql):
        return AskResponse(
            question=question,
            route="sql",
            answer="I couldn't answer that using the available data.",
            conversation_id="",
        )

    if not references_only_tenant_tables(sql, allowed_table_names):
        logger.error(
            "cross_tenant_sql_blocked tenant_id=%s sql=%r",
            tenant_id,
            sql,
        )

        return AskResponse(
            question=question,
            route="sql",
            answer="I couldn't answer that using the available data.",
            conversation_id="",
        )

    try:
        rows, total_count = execute_readonly_query(sql)
        query_id = store_query(sql)

        return AskResponse(
            question=question,
            route="sql",
            answer=f"Found {total_count} result(s).",
            data=rows,
            generated_sql=sql,
            conversation_id="",
            query_id=query_id,
        )

    except Exception as error:
        logger.error(
            "ask_sql_failed sql=%r error=%s",
            sql,
            error,
        )

        return AskResponse(
            question=question,
            route="sql",
            answer=(
                "Query execution failed. "
                "Please rephrase your question."
            ),
            conversation_id="",
        )


def _handle_document(
    question: str,
    history: list[dict],
    tenant_id: str,
) -> AskResponse:
    query_embedding = embed_query(question)

    results = search_chunks(
        query_embedding=query_embedding,
        tenant_id=tenant_id,
        top_k=5,
    )

    answer = generate_answer(
        question,
        results,
        history=history,
    )

    return AskResponse(
        question=question,
        route="document",
        answer=answer,
        sources=results,
        conversation_id="",
    )