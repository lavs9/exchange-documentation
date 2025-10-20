"""API endpoints for search functionality."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models import Document
from app.schemas.search import SearchQuery, SearchResults
from app.services.search_service_v2 import SearchError, SearchService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/documents/{document_id}/search",
    response_model=SearchResults,
    summary="Search within a document",
)
async def search_document(
    document_id: UUID,
    q: str = Query(..., min_length=1, description="Search query"),
    filter_type: str = Query(
        "all",
        regex="^(all|chapter|section)$",
        description="Filter by type: all, chapter, or section",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> SearchResults:
    """
    Search within a document using full-text search.

    This endpoint uses PostgreSQL's full-text search with:
    - **ts_rank** for relevance scoring
    - **ts_headline** for context snippets
    - **GIN index** for fast searching

    Args:
        document_id: Document UUID to search within
        q: Search query string
        filter_type: Filter results by type (all/chapter/section)
        page: Page number (1-indexed)
        page_size: Number of results per page (max 100)

    Returns:
        Search results with highlighted snippets and pagination
    """
    try:
        # Verify document exists
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}",
            )

        # Create search query
        search_query = SearchQuery(
            query=q,
            filter_type=filter_type,  # type: ignore
            page=page,
            page_size=page_size,
        )

        # Perform search
        search_service = SearchService(db)
        results = await search_service.search(document_id, search_query)

        return results

    except SearchError as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search operation failed: {str(e)}",
        )


@router.get(
    "/documents/{document_id}/search/suggestions",
    response_model=list[str],
    summary="Get search suggestions",
)
async def get_search_suggestions(
    document_id: UUID,
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of suggestions"),
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """
    Get search suggestions based on partial query.

    Uses section titles for autocomplete functionality.

    Args:
        document_id: Document UUID
        q: Partial search query
        limit: Maximum number of suggestions (max 10)

    Returns:
        List of suggested search terms
    """
    try:
        # Verify document exists
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}",
            )

        search_service = SearchService(db)
        suggestions = await search_service.get_suggestions(document_id, q, limit)

        return suggestions

    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}",
        )


@router.get(
    "/documents/{document_id}/search/page/{page_number}",
    response_model=list,
    summary="Get sections by page number",
)
async def search_by_page(
    document_id: UUID,
    page_number: int,
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    Get all sections from a specific page.

    Useful for navigation and page-based browsing.

    Args:
        document_id: Document UUID
        page_number: Page number (1-indexed)

    Returns:
        List of sections on the specified page
    """
    try:
        # Verify document exists
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}",
            )

        search_service = SearchService(db)
        results = await search_service.search_by_page(document_id, page_number)

        return results

    except Exception as e:
        logger.error(f"Page search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve page: {str(e)}",
        )


@router.get(
    "/documents/{document_id}/search/stats",
    response_model=dict,
    summary="Get search statistics",
)
async def get_search_stats(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get search statistics for a document.

    Returns information about total sections, pages, and content metrics.

    Args:
        document_id: Document UUID

    Returns:
        Dictionary with search statistics
    """
    try:
        # Verify document exists
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}",
            )

        search_service = SearchService(db)
        stats = await search_service.get_search_stats(document_id)

        return stats

    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}",
        )
