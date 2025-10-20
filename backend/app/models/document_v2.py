"""
Document model for file-based storage (v2).

This is the new lightweight model that stores only metadata.
Content is stored in files on disk.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):
    """
    Document metadata (file-based architecture).

    Content is stored in files at: storage/documents/{slug}/versions/{version}/
    This table only stores metadata for fast queries.
    """

    __tablename__ = "documents"

    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    active_version = Column(String(50), nullable=True)
    storage_path = Column(String(500), nullable=False)
    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=text("NOW()"),
        nullable=False,
    )

    # Relationships
    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    user_documents = relationship(
        "UserDocument",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, slug='{self.slug}', title='{self.title}')>"
