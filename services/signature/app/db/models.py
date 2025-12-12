from uuid_extensions import uuid7
from typing import ClassVar
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


class Signature(Base):
    __tablename__ = "signatures"
    __table_args__: ClassVar[dict] = {"schema": "signatures"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signer_name = Column(String(255), nullable=False)
    signed_at = Column(DateTime, default=datetime.utcnow)
    signature_data = Column(Text)  # Base64 encoded signature image or hash
    ip_address = Column(String(45))