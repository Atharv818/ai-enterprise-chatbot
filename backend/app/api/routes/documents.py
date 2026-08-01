import shutil
import uuid
from pathlib import Path
from app.services.ingestion import process_structured_file

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.session import get_db
from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)

_EXTENSION_MAP = {
    ".xlsx": DocumentType.XLSX,
    ".csv": DocumentType.CSV,
    ".pdf": DocumentType.PDF,
    ".docx": DocumentType.DOCX,
    ".txt": DocumentType.TXT,
}


@router.post("/upload", response_model=DocumentResponse)
def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    extension = Path(file.filename).suffix.lower()

    if extension not in _EXTENSION_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed: {list(_EXTENSION_MAP.keys())}",
        )

    document_id = str(uuid.uuid4())

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{document_id}{extension}"

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        id=document_id,
        filename=file.filename,
        file_type=_EXTENSION_MAP[extension],
        storage_path=str(destination),
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(f"document_uploaded id={document.id} filename={document.filename}")

    if document.file_type in (DocumentType.XLSX, DocumentType.CSV):
        document.status = DocumentStatus.PROCESSING
        db.commit()
        process_structured_file(document, db)
        db.refresh(document)

    return document