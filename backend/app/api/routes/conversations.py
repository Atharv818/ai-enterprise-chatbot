from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth_dependency import get_current_tenant_id
from app.db.session import get_db
from app.models.conversation import Conversation, Message
from app.schemas.conversation import ConversationDetail, ConversationSummary, MessageResponse

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
def list_conversations(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_tenant_id)):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.tenant_id == tenant_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    summaries = []
    for conv in conversations:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .all()
        )
        last_message = messages[0].content if messages else None
        summaries.append(
            ConversationSummary(
                id=conv.id,
                created_at=conv.created_at,
                last_message=last_message,
                message_count=len(messages),
            )
        )
    return summaries


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_tenant_id)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return ConversationDetail(
        id=conversation.id,
        created_at=conversation.created_at,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_tenant_id)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.delete(conversation)
    db.commit()
    