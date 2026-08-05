from fastapi import FastAPI
from app.api.routes import documents
from app.core.config import settings
from app.core.logging_config import configure_logging, get_logger
from app.api.routes import documents, query
from app.db.qdrant_client import qdrant
from app.api.routes import documents, query, search
from app.api.routes import ask, documents, query, search
from app.api.routes import ask, chat, documents, query, search
from app.api.routes import ask, conversations, documents, query, search

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.on_event("startup")
def on_startup():
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up")


app.include_router(documents.router)
app.include_router(query.router)
app.include_router(search.router)
app.include_router(ask.router)
app.include_router(chat.router)
app.include_router(conversations.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/qdrant")
def qdrant_health():
    collections = qdrant.get_collections()
    return {"status": "ok", "collections": [c.name for c in collections.collections]}

