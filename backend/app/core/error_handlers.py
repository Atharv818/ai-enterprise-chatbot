from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"unhandled_exception path={request.url.path} error={exc!r}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )
