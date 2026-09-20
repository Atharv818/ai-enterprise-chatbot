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
from app.services.text_extraction import extract_text
from app.services.chunking import chunk_text, chunk_params_label
from app.services.embedding import embed_chunks
from app.services.vector_store import store_chunks, delete_chunks
from app.services.hashing import compute_file_hash
from app.core.auth_dependency import get_current_tenant_id
from app.core.tenant_scoped import create_tenant_scoped


router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)

_EXTENSION_MAP = {
    ".xlsx": DocumentType.XLSX,
    ".csv": DocumentType.CSV,
    ".pdf": DocumentType.PDF,
    ".docx": DocumentType.DOCX,
    ".txt": DocumentType.TXT,
}

_TEXT_TYPES = (DocumentType.PDF, DocumentType.DOCX, DocumentType.TXT)
_STRUCTURED_TYPES = (DocumentType.XLSX, DocumentType.CSV)


def _find_duplicate(db: Session, tenant_id: str, file_hash: str) -> Document | None:
    return (
        db.query(Document)
        .filter(
            Document.tenant_id == tenant_id,
            Document.content_hash == file_hash,
            Document.status != DocumentStatus.FAILED,
        )
        .order_by(Document.uploaded_at.desc())
        .first()
    )


def _duplicate_detail(existing: Document) -> dict:
    is_stale = existing.file_type in _TEXT_TYPES and existing.chunk_params != chunk_params_label()
    return {
        "message": "This file has already been uploaded.",
        "document_id": existing.id,
        "filename": existing.filename,
        "uploaded_at": existing.uploaded_at.isoformat(),
        "status": existing.status.value,
        "can_reprocess": True,
        "reprocess_recommended": is_stale,
    }


@router.post("/upload", response_model=DocumentResponse)
def upload_document(file: UploadFile, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_tenant_id)):
    extension = Path(file.filename).suffix.lower()

    if extension not in _EXTENSION_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed: {list(_EXTENSION_MAP.keys())}",
        )

    content = file.file.read()
    file_hash = compute_file_hash(content)

    existing = _find_duplicate(db, tenant_id, file_hash)
    if existing:
        logger.info(f"duplicate_upload_blocked tenant={tenant_id} existing_id={existing.id}")
        raise HTTPException(status_code=409, detail=_duplicate_detail(existing))

    document_id = str(uuid.uuid4())

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{document_id}{extension}"

    with destination.open("wb") as buffer:
        buffer.write(content)

    document = create_tenant_scoped(
        Document,
        tenant_id,
        id=document_id,
        filename=file.filename,
        file_type=_EXTENSION_MAP[extension],
        storage_path=str(destination),
        status=DocumentStatus.PENDING,
        content_hash=file_hash,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(f"document_uploaded id={document.id} filename={document.filename}")

    if document.file_type in _STRUCTURED_TYPES:
        document.status = DocumentStatus.PROCESSING
        db.commit()
        process_structured_file(document, db, tenant_id)
        db.refresh(document)
    elif document.file_type in _TEXT_TYPES:
        document.status = DocumentStatus.PROCESSING
        db.commit()
        try:
            text = extract_text(document.storage_path, document.file_type.value)
            chunks = chunk_text(text)
            embeddings = embed_chunks(chunks)
            stored_count = store_chunks(document.id, tenant_id, chunks, embeddings)
            logger.info(f"document_indexed id={document.id} chunks={stored_count}")
            document.chunk_params = chunk_params_label()
            document.status = DocumentStatus.READY
        except Exception as e:  # noqa: BLE001
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            logger.error(f"document_indexing_failed id={document.id} error={e}")
        db.commit()
        db.refresh(document)

    return document


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
def reprocess_document(
    document_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_tenant_id)
):
    """Re-runs ingestion/chunking on an already-uploaded file, without
    requiring the bytes to be sent again (they're identical by definition —
    this only exists because the content hash matched on a prior upload
    attempt). Used to bring old documents up to current chunk params, or to
    retry a FAILED document."""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.tenant_id == tenant_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = DocumentStatus.PROCESSING
    document.error_message = None
    db.commit()

    if document.file_type in _STRUCTURED_TYPES:
        # ingestion.py uses if_exists="replace", so this safely rebuilds the table
        process_structured_file(document, db, tenant_id)
        db.refresh(document)
    else:
        try:
            delete_chunks(document.id, tenant_id)
            text = extract_text(document.storage_path, document.file_type.value)
            chunks = chunk_text(text)
            embeddings = embed_chunks(chunks)
            stored_count = store_chunks(document.id, tenant_id, chunks, embeddings)
            logger.info(f"document_reindexed id={document.id} chunks={stored_count}")
            document.chunk_params = chunk_params_label()
            document.status = DocumentStatus.READY
        except Exception as e:  # noqa: BLE001
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            logger.error(f"document_reprocessing_failed id={document.id} error={e}")
        db.commit()
        db.refresh(document)

    return document