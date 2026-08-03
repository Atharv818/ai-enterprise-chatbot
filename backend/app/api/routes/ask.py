from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.models.ingested_table import IngestedTable
from app.services.embedding import embed_query
from app.services.nl_to_sql import generate_sql
from app.services.query_executor import execute_readonly_query
from app.services.query_router import classify_question
from app.services.rag_answer import generate_answer
from app.services.schema_context import build_schema_context
from app.services.sql_safety import is_safe_select
from app.services.vector_store import search_chunks
from app.schemas.ask import AskRequest, AskResponse

router = APIRouter(prefix="/ask", tags=["ask"])
logger = get_logger(__name__)


@router.post("", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)):
    has_tables = db.query(IngestedTable).first() is not None
    has_documents = _has_indexed_documents()

    if has_tables and not has_documents:
        route = "sql"
    elif has_documents and not has_tables:
        route = "document"
    elif has_tables and has_documents:
        route = classify_question(request.question)
    else:
        return AskResponse(
            question=request.question,
            route="none",
            answer="No data has been uploaded yet. Please upload a document or spreadsheet first.",
        )

    logger.info(f"ask_routed question={request.question!r} route={route}")

    if route == "sql":
        return _handle_sql(request.question, db)
    else:
        return _handle_document(request.question)


def _has_indexed_documents() -> bool:
    from app.db.qdrant_client import qdrant
    from app.services.vector_store import COLLECTION_NAME

    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        return False
    info = qdrant.get_collection(COLLECTION_NAME)
    return info.points_count > 0


def _handle_sql(question: str, db: Session) -> AskResponse:
    schema_context = build_schema_context(db)
    sql = generate_sql(question, schema_context)

    if "UNSUPPORTED_QUERY" in sql or not is_safe_select(sql):
        return AskResponse(question=question, route="sql", answer="I couldn't answer that using the available data.")

    try:
        rows, total_count = execute_readonly_query(sql)
        return AskResponse(
            question=question,
            route="sql",
            answer=f"Found {total_count} result(s).",
            data=rows,
            generated_sql=sql,
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"ask_sql_failed sql={sql!r} error={e}")
        return AskResponse(question=question, route="sql", answer="Query execution failed. Please rephrase your question.")


def _handle_document(question: str) -> AskResponse:
    query_embedding = embed_query(question)
    results = search_chunks(query_embedding=query_embedding, top_k=5)
    answer = generate_answer(question, results)
    return AskResponse(question=question, route="document", answer=answer, sources=results)

