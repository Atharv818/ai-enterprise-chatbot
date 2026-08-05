from datetime import datetime

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    route: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    id: str
    created_at: datetime
    last_message: str | None
    message_count: int


class ConversationDetail(BaseModel):
    id: str
    created_at: datetime
    messages: list[MessageResponse]

    