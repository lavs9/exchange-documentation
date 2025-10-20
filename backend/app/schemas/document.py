"""Pydantic schemas for document-related requests and responses."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SectionBase(BaseModel):
    """Base schema for section."""

    level: int = Field(..., ge=1, le=6, description="Heading level (1-6)")
    title: str = Field(..., min_length=1, max_length=500, description="Section title")
    content: str = Field(..., description="Section content in markdown")
    page_number: Optional[int] = Field(None, ge=1, description="Page number in PDF")
    parent_id: Optional[UUID] = Field(None, description="Parent section ID")
    order_index: int = Field(..., ge=0, description="Order within document")


class SectionCreate(SectionBase):
    """Schema for creating a section."""

    document_id: UUID = Field(..., description="Document ID")


class SectionResponse(SectionBase):
    """Schema for section response."""

    id: UUID = Field(..., description="Section ID")
    document_id: UUID = Field(..., description="Document ID")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentBase(BaseModel):
    """Base schema for document."""

    title: str = Field(..., min_length=1, max_length=255, description="Document title")
    version: str = Field(..., min_length=1, max_length=50, description="Document version")


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    id: UUID = Field(..., description="Document ID")
    upload_date: datetime
    file_path: str
    page_count: Optional[int] = None
    processing_status: str = Field(..., description="Processing status")
    metadata: Optional[dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class DocumentWithSections(DocumentResponse):
    """Schema for document with sections."""

    sections: list[SectionResponse] = Field(default_factory=list)


class DocumentList(BaseModel):
    """Schema for paginated document list."""

    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int


class ProcessingStatus(BaseModel):
    """Schema for document processing status."""

    document_id: UUID
    status: str = Field(..., description="Processing status: pending, processing, completed, failed")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Processing progress percentage")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class TOCEntry(BaseModel):
    """Schema for table of contents entry."""

    id: UUID
    title: str
    level: int
    page_number: Optional[int] = None
    children: list["TOCEntry"] = Field(default_factory=list)


class TableOfContents(BaseModel):
    """Schema for complete table of contents."""

    document_id: UUID
    entries: list[TOCEntry]
