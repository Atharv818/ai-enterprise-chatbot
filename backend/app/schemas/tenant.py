from datetime import datetime

from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str


class TenantResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
        