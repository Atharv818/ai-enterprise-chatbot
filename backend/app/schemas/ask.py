from typing import Any

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    route: str
    answer: str
    data: list[dict[str, Any]] | None = None
    sources: list[dict[str, Any]] | None = None
    generated_sql: str | None = None

    