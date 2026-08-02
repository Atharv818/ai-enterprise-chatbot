from typing import Any

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    generated_sql: str
    results: list[dict[str, Any]] | None = None
    total_rows: int | None = None
    truncated: bool = False
    error: str | None = None

    