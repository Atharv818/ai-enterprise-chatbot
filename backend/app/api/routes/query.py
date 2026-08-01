from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.nl_to_sql import generate_sql
from app.services.schema_context import build_schema_context

router = APIRouter(prefix="/query", tags=["query"])
logger = get_logger(__name__)


@router.post("/generate-sql", response_model=QueryResponse)
def generate_sql_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    schema_context = build_schema_context(db)
    sql = generate_sql(request.question, schema_context)

    logger.info(f"sql_generated question={request.question!r} sql={sql!r}")

    return QueryResponse(question=request.question, generated_sql=sql)

