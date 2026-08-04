from typing import Any

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    conversation_id: str | None = None


class AskResponse(BaseModel):
    question: str
    route: str
    answer: str
    conversation_id: str
    data: list[dict[str, Any]] | None = None
    sources: list[dict[str, Any]] | None = None
    generated_sql: str | None = None
    
    