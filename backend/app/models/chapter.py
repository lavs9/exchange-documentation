"""
Chapter model for file-based storage.

Stores metadata and search index - content is in files.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, TSVECTOR
from sqlalchemy.orm import relationship

from app.core.database import Base


class Chapter(Base):
    """
    Chapter metadata and search index (file-based architecture).

    Content is stored in files at:
    storage/documents/{doc-slug}/versions/{version}/chapters/chapter-{num}-{slug}.md

    This table stores:
    - Metadata (title, page_range, word_count, etc.)
    - Search index (search_vector for PostgreSQL full-text search)
    - File path (to read actual content from disk)
    """

    __tablename__ = "chapters"

    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    version_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chapter_number = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=False)  # Relative path from base storage
    page_range = Column(String(50), nullable=True)  # e.g., "46-72"
    word_count = Column(Integer, server_default=text("0"), nullable=False)
    has_manual_content = Column(Boolean, server_default=text("false"), nullable=False)
    has_linked_docs = Column(Boolean, server_default=text("false"), nullable=False)
    search_vector = Column(TSVECTOR, nullable=True)  # For full-text search
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
    version = relationship("DocumentVersion", back_populates="chapters")

    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, number={self.chapter_number}, title='{self.title}')>"
