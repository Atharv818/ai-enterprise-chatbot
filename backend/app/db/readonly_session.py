from sqlalchemy import create_engine

from app.core.config import settings

readonly_engine = create_engine(settings.READONLY_DATABASE_URL, pool_pre_ping=True)
