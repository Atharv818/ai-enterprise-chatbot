import re
import logging

logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter", "truncate",
    "create", "grant", "revoke", "execute", "call", "merge",
]


def is_safe_select(sql: str) -> bool:
    """
    Returns True only if the query is a single, simple SELECT statement
    with no destructive or write keywords anywhere in it.
    """
    cleaned = sql.strip().rstrip(";").strip()

    if not cleaned.lower().startswith("select"):
        logger.warning(f"sql_safety_rejected reason=not_select sql={sql!r}")
        return False

    # Reject multiple statements (e.g. "SELECT 1; DROP TABLE x;")
    if ";" in cleaned:
        logger.warning(f"sql_safety_rejected reason=multiple_statements sql={sql!r}")
        return False

    lowered = cleaned.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lowered):
            logger.warning(f"sql_safety_rejected reason=forbidden_keyword keyword={keyword!r} sql={sql!r}")
            return False

    logger.info(f"sql_safety_passed sql={sql!r}")
    return True


def references_only_tenant_tables(sql: str, allowed_table_names: list[str]) -> bool:
    """
    Ensures the SQL only references table names this tenant actually owns.
    A crude but effective check: every doc_{uuid}-style table name mentioned
    in the SQL must be in the tenant's allowed list.
    """
    mentioned_doc_tables = re.findall(r'\bdoc_[a-f0-9_]{20,}\b', sql.lower())
    result = all(table in allowed_table_names for table in mentioned_doc_tables)
    if not result:
        disallowed = [t for t in mentioned_doc_tables if t not in allowed_table_names]
        logger.warning(f"tenant_table_check_rejected disallowed_tables={disallowed} sql={sql!r}")
    return result