"""Pydantic schemas for search-related requests and responses."""
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Schema for search query parameters."""

    query: str = Field(..., min_length=1, description="Search query string")
    filter_type: Literal["all", "chapter", "section"] = Field(
        default="all", description="Filter results by type"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class SearchResult(BaseModel):
    """Schema for individual search result."""

    section_id: UUID = Field(..., description="Section ID")
    document_id: UUID = Field(..., description="Document ID")
    title: str = Field(..., description="Section title")
    snippet: str = Field(..., description="Content snippet with highlighted terms")
    page_number: Optional[int] = Field(None, description="Page number in PDF")
    rank: float = Field(..., description="Search relevance rank")
    level: int = Field(..., description="Section level")


class SearchResults(BaseModel):
    """Schema for search results with pagination."""

    results: list[SearchResult]
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    query: str = Field(..., description="Original search query")


class SearchStats(BaseModel):
    """Schema for search statistics."""

    total_sections: int
    total_documents: int
    avg_query_time_ms: float
