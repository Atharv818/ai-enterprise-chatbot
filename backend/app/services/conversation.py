from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.core.tenant_scoped import create_tenant_scoped

MAX_HISTORY_MESSAGES = 6  # last 3 user/assistant turns


def get_or_create_conversation(db: Session, conversation_id: str | None, tenant_id: str) -> Conversation:
    if conversation_id:
        existing = db.get(Conversation, conversation_id)
        if existing and existing.tenant_id == tenant_id:
            return existing
    conversation = create_tenant_scoped(Conversation, tenant_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_recent_history(db: Session, conversation_id: str) -> list[dict]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
        .all()
    )
    messages.reverse()  # chronological order
    return [{"role": m.role, "content": m.content} for m in messages]


def save_message(db: Session, conversation_id: str, role: str, content: str, route: str | None = None) -> None:
    message = Message(conversation_id=conversation_id, role=role, content=content, route=route)
    db.add(message)
    db.commit()

def get_last_route(db: Session, conversation_id: str) -> str | None:
    last_assistant_message = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id, Message.role == "assistant")
        .order_by(Message.created_at.desc())
        .first()
    )
    return last_assistant_message.route if last_assistant_message else None

