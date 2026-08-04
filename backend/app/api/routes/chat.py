from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.routes.ask import _handle_sql, _handle_document, _has_indexed_documents
from app.models.ingested_table import IngestedTable
from app.services.query_router import classify_question

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if request.conversation_id:
        conversation = db.get(Conversation, request.conversation_id)
        if conversation is None:
            conversation = Conversation()
            db.add(conversation)
            db.commit()
    else:
        conversation = Conversation()
        db.add(conversation)
        db.commit()

    history_rows = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in history_rows]

    db.add(Message(conversation_id=conversation.id, role="user", content=request.message))
    db.commit()

    has_tables = db.query(IngestedTable).first() is not None
    has_documents = _has_indexed_documents()

    if has_tables and not has_documents:
        route = "sql"
    elif has_documents and not has_tables:
        route = "document"
    elif has_tables and has_documents:
        route = classify_question(request.message, history)
    else:
        route = "none"

    if route == "sql":
        result = _handle_sql(request.message, db)
        answer = result.answer
    elif route == "document":
        result = _handle_document(request.message)
        answer = result.answer
    else:
        answer = "No data has been uploaded yet. Please upload a document or spreadsheet first."

    db.add(Message(conversation_id=conversation.id, role="assistant", content=answer, route=route))
    db.commit()

    logger.info(f"chat_message conversation_id={conversation.id} route={route}")

    return ChatResponse(conversation_id=conversation.id, answer=answer, route=route)


