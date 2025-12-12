from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

class SignatureCreate(BaseModel):
    """Schema for creating a signature."""
    document_id: UUID
    signer_email: EmailStr
    signer_name: str = Field(..., min_length=1, max_length=255)
    signature_data: str | None = None
    ip_address: str | None = None

    @validator("signature_data")
    def validate_signature_size(cls,v):
        """Limit signature data to 1MB."""
        if v:
            max_size=1*1024*1024
            if len(v)>max_size:
                raise ValueError('Signature data exceeds 1MB limit')
        return v


class SignatureResponse(BaseModel):
    """Schema for signature response."""
    id: UUID
    document_id:UUID
    signer_email: str
    signer_name: str
    signed_at: datetime
    signature_data: str | None = None
    ip_address: str | None = None

    class Config:
        from_attributes = True