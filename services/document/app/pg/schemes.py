from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from .models import DocumentStatus

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    content_type: str = "text/plain"
    created_by: EmailStr

    @field_validator("content")
    def validate_content_size(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 10 * 1024 * 1024:  # 10 MB limit
            raise ValueError("Content size exceeds 10 MB limit")
        return v


class DocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    status: DocumentStatus | None = None

class DocumentResponse(BaseModel):
    id: UUID
    title: str
    content_type: str
    content_size: int
    s3_key: str | None
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True
        