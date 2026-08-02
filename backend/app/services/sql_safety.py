import re

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
        return False

    # Reject multiple statements (e.g. "SELECT 1; DROP TABLE x;")
    if ";" in cleaned:
        return False

    lowered = cleaned.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lowered):
            return False

    return True
