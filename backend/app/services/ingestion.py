import json
import re

import pandas as pd
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import engine
from app.models.document import Document, DocumentStatus
from app.models.ingested_table import IngestedTable

logger = get_logger(__name__)


def _sanitize_identifier(raw: str) -> str:
    """Turn an arbitrary spreadsheet header into a safe SQL column name."""
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", raw.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "col"
    if cleaned[0].isdigit():
        cleaned = f"c_{cleaned}"
    return cleaned


def process_structured_file(document: Document, db: Session) -> None:
    """
    Reads an uploaded xlsx/csv file, creates a dedicated SQL table for it,
    and inserts every row. Updates the document's status to READY or FAILED.
    """
    try:
        if document.file_type.value == "csv":
            df = pd.read_csv(document.storage_path)
        else:
            df = pd.read_excel(document.storage_path)

        df.columns = [_sanitize_identifier(str(c)) for c in df.columns]

        table_name = f"doc_{document.id.replace('-', '_')}"
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)

        column_schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
        ingested = IngestedTable(
            document_id=document.id,
            table_name=table_name,
            column_schema=json.dumps(column_schema),
            row_count=len(df),
        )
        db.add(ingested)

        document.status = DocumentStatus.READY
        logger.info(f"document_processed id={document.id} table={table_name} rows={len(df)}")

    except Exception as e:  # noqa: BLE001
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        logger.error(f"document_processing_failed id={document.id} error={e}")

    db.commit()