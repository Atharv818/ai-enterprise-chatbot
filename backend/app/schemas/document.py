from datetime import datetime

from pydantic import BaseModel

from app.models.document import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: DocumentType
    status: DocumentStatus
    uploaded_at: datetime

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy object directly