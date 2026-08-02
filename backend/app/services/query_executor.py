from sqlalchemy import text

from app.db.readonly_session import readonly_engine
from app.core.logging_config import get_logger

logger = get_logger(__name__)

MAX_INLINE_ROWS = 10


def execute_readonly_query(sql: str, limit: int | None = MAX_INLINE_ROWS) -> tuple[list[dict], int]:
    """
    Executes a SELECT query using the read-only database connection.
    Returns (rows, total_row_count).
    If limit is None, returns every row (used for CSV export).
    """
    with readonly_engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = result.keys()

        if limit is None:
            all_rows = result.fetchall()
        else:
            all_rows = result.fetchmany(limit)

        rows = [dict(zip(columns, row)) for row in all_rows]

    # Get the true total count separately, since fetchmany() only tells us what we grabbed
    with readonly_engine.connect() as conn:
        count_result = conn.execute(text(f"SELECT COUNT(*) FROM ({sql.rstrip(';')}) AS subquery"))
        total_count = count_result.scalar()

    return rows, total_count

