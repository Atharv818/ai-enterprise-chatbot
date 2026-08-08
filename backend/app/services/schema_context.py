import json

from sqlalchemy.orm import Session

from app.models.ingested_table import IngestedTable


def build_schema_context(db: Session, tenant_id: str) -> str:
    """
    Builds a plain-text description of every ingested table and its columns,
    scoped to a single tenant, for the AI to use when generating SQL.
    """
    tables = db.query(IngestedTable).filter(IngestedTable.tenant_id == tenant_id).all()

    if not tables:
        return "No tables are currently available."

    lines = []
    for table in tables:
        columns = json.loads(table.column_schema)
        column_list = ", ".join(f"{col} ({dtype})" for col, dtype in columns.items())
        lines.append(f"Table \"{table.table_name}\" ({table.row_count} rows): {column_list}")

    return "\n".join(lines)
