import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.nl_to_sql import generate_sql
from app.services.query_cache import get_query, store_query
from app.services.query_executor import execute_readonly_query
from app.services.schema_context import build_schema_context
from app.services.sql_safety import is_safe_select

router = APIRouter(prefix="/query", tags=["query"])
logger = get_logger(__name__)


@router.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    schema_context = build_schema_context(db)
    sql = generate_sql(request.question, schema_context)

    logger.info(f"sql_generated question={request.question!r} sql={sql!r}")

    if "UNSUPPORTED_QUERY" in sql:
        return QueryResponse(
            question=request.question,
            generated_sql=sql,
            error="This question can't be answered with the currently available data.",
        )

    if not is_safe_select(sql):
        logger.error(f"unsafe_sql_blocked sql={sql!r}")
        return QueryResponse(
            question=request.question,
            generated_sql=sql,
            error="Generated query failed safety validation and was not executed.",
        )

    try:
        rows, total_count = execute_readonly_query(sql)
        query_id = store_query(sql)
        return QueryResponse(
            question=request.question,
            generated_sql=f"{sql} [query_id={query_id}]",
            results=rows,
            total_rows=total_count,
            truncated=total_count > len(rows),
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"query_execution_failed sql={sql!r} error={e}")
        return QueryResponse(
            question=request.question,
            generated_sql=sql,
            error="Query execution failed. Please rephrase your question.",
        )


@router.get("/export/{query_id}")
def export_query_csv(query_id: str):
    sql = get_query(query_id)
    if sql is None:
        raise HTTPException(status_code=404, detail="Query not found or has expired.")

    rows, _ = execute_readonly_query(sql, limit=None)

    if not rows:
        raise HTTPException(status_code=404, detail="No data to export.")

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=export_{query_id}.csv"},
    )

