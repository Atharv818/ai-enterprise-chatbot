from fastapi import FastAPI
from app.core.config import settings
from app.core.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.on_event("startup")
def on_startup():
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up")


@app.get("/health")
def health_check():
    return {"status": "ok"}