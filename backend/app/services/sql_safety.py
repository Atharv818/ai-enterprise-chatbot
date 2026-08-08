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

def references_only_tenant_tables(sql: str, allowed_table_names: list[str]) -> bool:
    """
    Ensures the SQL only references table names this tenant actually owns.
    A crude but effective check: every doc_{uuid}-style table name mentioned
    in the SQL must be in the tenant's allowed list.
    """
    import re
    mentioned_doc_tables = re.findall(r'\bdoc_[a-f0-9_]{20,}\b', sql.lower())
    return all(table in allowed_table_names for table in mentioned_doc_tables)