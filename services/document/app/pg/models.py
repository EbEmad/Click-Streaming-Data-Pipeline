from enum import Enum

from uuid_extensions import uuid7
from datetime import datetime
from typing import ClassVar

from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class DocumentStatus(str,Enum):
    CREATED = "created"
    SENT = "sent"
    VIEWED = "viewed"
    SIGNED = "signed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class Document(Base):
    __tablename__ = "documents"
    __table_args__: ClassVar[dict] = {"schema": "documents"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    title = Column(String(255), nullable=False)
    content_type = Column(String(100), default="text/plain")
    content_size = Column(BigInteger, default=0)  # Size in bytes
    s3_key = Column(String(500))  # S3 object key
    status = Column(String(50), nullable=False, default=DocumentStatus.CREATED.value)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)