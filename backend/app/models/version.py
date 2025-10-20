"""
DocumentVersion model for file-based storage.

Tracks versions of documents with metadata stored in files.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class DocumentVersion(Base):
    """
    Document version metadata (file-based architecture).

    Each version has its own directory with chapters/ and links/ subdirectories.
    """

    __tablename__ = "document_versions"

    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    document_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(String(50), nullable=False)
    status = Column(
        String(20),
        nullable=False,
        index=True,
    )
    metadata_file_path = Column(String(500), nullable=True)
    upload_date = Column(
        TIMESTAMP,
        server_default=text("NOW()"),
        nullable=False,
    )
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_version_status",
        ),
    )

    # Relationships
    document = relationship("Document", back_populates="versions")
    chapters = relationship(
        "Chapter",
        back_populates="version",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DocumentVersion(id={self.id}, version='{self.version}', status='{self.status}')>"
