"""SQLAlchemy model for user-created documents (notes and references)."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, text, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, TSVECTOR
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserDocument(Base):
    """
    User-created document (note or reference).

    Content is stored in markdown files (notes/ or references/ directories).
    This table stores metadata and search index only.
    """

    __tablename__ = "user_documents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    document_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    version = Column(String(50), nullable=False, index=True)
    file_path = Column(String(500), nullable=False, index=True)  # e.g., "notes/order-validation-tips.md"
    title = Column(Text, nullable=False)
    doc_type = Column(String(20), nullable=False, index=True)  # "note" or "reference"
    search_vector = Column(TSVECTOR)  # For full-text search
    created_by = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("NOW()"))
    tags = Column(ARRAY(Text), nullable=True)

    # Relationship to parent document
    document = relationship("Document", back_populates="user_documents")

    def __repr__(self) -> str:
        return f"<UserDocument(id={self.id}, title='{self.title}', type='{self.doc_type}')>"
