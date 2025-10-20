"""
Full-text search service using PostgreSQL (file-based storage version).

This version searches the chapters table instead of sections.
The search_vector is still stored in the database for fast searching,
while the actual content is in files.
"""
import logging
from typing import Literal
from uuid import UUID

from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Document, DocumentVersion, Chapter
from app.schemas.search import SearchQuery, SearchResult, SearchResults

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Raised when search operation fails."""
    pass


class SearchService:
    """PostgreSQL full-text search service for file-based storage."""

    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initialize search service.

        Args:
            db_session: Database session
        """
        self._db = db_session

    async def search(
        self,
        document_id: UUID,
        query_params: SearchQuery,
    ) -> SearchResults:
        """
        Perform full-text search on document chapters.

        Uses PostgreSQL's tsvector and ts_rank for relevance-based search.
        Search index is in database, actual content is in files.

        Args:
            document_id: Document ID to search within
            query_params: Search query parameters

        Returns:
            SearchResults with ranked results and snippets

        Raises:
            SearchError: If search fails
        """
        try:
            logger.info(
                f"Searching document {document_id} for '{query_params.query}'"
            )

            # Get document and active version
            document = await self._db.get(Document, document_id)
            if not document or not document.active_version:
                return SearchResults(
                    results=[],
                    total=0,
                    page=query_params.page,
                    page_size=query_params.page_size,
                    query=query_params.query,
                )

            result = await self._db.execute(
                select(DocumentVersion).where(
                    DocumentVersion.document_id == document_id,
                    DocumentVersion.version == document.active_version
                )
            )
            version = result.scalar_one_or_none()
            if not version:
                return SearchResults(
                    results=[],
                    total=0,
                    page=query_params.page,
                    page_size=query_params.page_size,
                    query=query_params.query,
                )

            # Build and execute search query
            snippet_words = settings.search_result_snippet_size
            search_query = text(f"""
                SELECT
                    c.id,
                    c.title,
                    ts_headline(
                        'english',
                        c.title || ' ',
                        plainto_tsquery('english', :search_term),
                        'MaxWords={snippet_words}, MinWords=10'
                    ) as snippet,
                    c.page_range,
                    ts_rank(c.search_vector, plainto_tsquery('english', :search_term)) as rank,
                    1 as level
                FROM chapters c
                WHERE c.version_id = :version_id
                    AND c.search_vector @@ plainto_tsquery('english', :search_term)
                ORDER BY rank DESC, c.chapter_number ASC
                LIMIT :limit OFFSET :offset
            """)

            # Calculate offset for pagination
            offset = (query_params.page - 1) * query_params.page_size

            # Execute search
            search_result = await self._db.execute(
                search_query,
                {
                    "version_id": str(version.id),
                    "search_term": query_params.query,
                    "limit": query_params.page_size,
                    "offset": offset,
                },
            )

            rows = search_result.fetchall()

            # Convert to SearchResult objects
            search_results = []
            for row in rows:
                # Extract page number from page_range (e.g., "12-45" -> 12)
                page_number = None
                if row[3]:
                    try:
                        page_number = int(row[3].split('-')[0])
                    except:
                        pass

                search_results.append(
                    SearchResult(
                        section_id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
                        document_id=document_id,
                        title=row[1],
                        snippet=row[2],
                        page_number=page_number,
                        rank=float(row[4]),
                        level=row[5],
                    )
                )

            # Get total count
            total = await self._get_total_count(version.id, query_params.query)

            logger.info(
                f"Found {total} results, returning {len(search_results)} for page {query_params.page}"
            )

            return SearchResults(
                results=search_results,
                total=total,
                page=query_params.page,
                page_size=query_params.page_size,
                query=query_params.query,
            )

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            raise SearchError(f"Search operation failed: {str(e)}") from e

    async def _get_total_count(self, version_id: UUID, search_term: str) -> int:
        """Get total count of search results."""
        try:
            count_query = text("""
                SELECT COUNT(*)
                FROM chapters c
                WHERE c.version_id = :version_id
                    AND c.search_vector @@ plainto_tsquery('english', :search_term)
            """)

            result = await self._db.execute(
                count_query,
                {
                    "version_id": str(version_id),
                    "search_term": search_term,
                },
            )

            count = result.scalar()
            return count or 0

        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            return 0
