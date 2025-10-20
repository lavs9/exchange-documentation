"""Full-text search service using PostgreSQL."""
import logging
from typing import Literal, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.search import SearchQuery, SearchResult, SearchResults

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Raised when search operation fails."""

    pass


class SearchService:
    """PostgreSQL full-text search service."""

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
        Perform full-text search on document sections.

        Uses PostgreSQL's tsvector and ts_rank for relevance-based search.

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

            # Build SQL query based on filter type
            sql_query = self._build_search_query(query_params.filter_type)

            # Calculate offset for pagination
            offset = (query_params.page - 1) * query_params.page_size

            # Execute search
            result = await self._db.execute(
                sql_query,
                {
                    "document_id": str(document_id),
                    "search_term": query_params.query,
                    "snippet_words": settings.search_result_snippet_size,
                    "limit": query_params.page_size,
                    "offset": offset,
                },
            )

            rows = result.fetchall()

            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    section_id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
                    document_id=document_id,
                    title=row[1],
                    snippet=row[2],
                    page_number=row[3],
                    rank=float(row[4]),
                    level=row[5],
                )
                for row in rows
            ]

            # Get total count
            total = await self._get_total_count(document_id, query_params.query)

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

    def _build_search_query(
        self, filter_type: Literal["all", "chapter", "section"]
    ) -> text:
        """
        Build SQL query based on filter type.

        Args:
            filter_type: Type of sections to filter

        Returns:
            SQL query text
        """
        # Base query with full-text search
        base_query = """
            SELECT
                s.id,
                s.title,
                ts_headline('english', s.content, query,
                    'MaxWords=50, MinWords=10, HighlightAll=false') as snippet,
                s.page_number,
                ts_rank(s.search_vector, query) as rank,
                s.level
            FROM
                sections s,
                plainto_tsquery('english', :search_term) query
            WHERE
                s.document_id = :document_id
                AND s.search_vector @@ query
        """

        # Add filter based on type
        if filter_type == "chapter":
            # Only level 1 (chapters)
            base_query += " AND s.level = 1"
        elif filter_type == "section":
            # Level 2 and below (sections and subsections)
            base_query += " AND s.level >= 2"
        # 'all' - no additional filter

        # Add ordering and pagination
        base_query += """
            ORDER BY rank DESC, s.order_index
            LIMIT :limit OFFSET :offset
        """

        return text(base_query)

    async def _get_total_count(self, document_id: UUID, search_term: str) -> int:
        """
        Get total count of matching results.

        Args:
            document_id: Document ID
            search_term: Search query

        Returns:
            Total number of matching sections
        """
        count_query = text("""
            SELECT COUNT(*)
            FROM
                sections s,
                plainto_tsquery('english', :search_term) query
            WHERE
                s.document_id = :document_id
                AND s.search_vector @@ query
        """)

        result = await self._db.execute(
            count_query,
            {"document_id": str(document_id), "search_term": search_term},
        )

        row = result.fetchone()
        return row[0] if row else 0

    async def highlight_terms(
        self, content: str, search_term: str
    ) -> str:
        """
        Highlight search terms in content using PostgreSQL ts_headline.

        Args:
            content: Original content
            search_term: Search terms to highlight

        Returns:
            Content with highlighted terms (HTML markup)
        """
        try:
            highlight_query = text("""
                SELECT ts_headline('english', :content, query,
                    'MaxFragments=3, FragmentDelimiter=...')
                FROM plainto_tsquery('english', :search_term) query
            """)

            result = await self._db.execute(
                highlight_query,
                {"content": content, "search_term": search_term},
            )

            row = result.fetchone()
            return row[0] if row else content

        except Exception as e:
            logger.error(f"Highlighting failed: {e}", exc_info=True)
            return content  # Return original on error

    async def get_suggestions(
        self, document_id: UUID, partial_query: str, limit: int = 5
    ) -> list[str]:
        """
        Get search suggestions based on partial query.

        Uses section titles for autocomplete suggestions.

        Args:
            document_id: Document ID
            partial_query: Partial search term
            limit: Maximum number of suggestions

        Returns:
            List of suggested search terms
        """
        try:
            suggestion_query = text("""
                SELECT DISTINCT s.title
                FROM sections s
                WHERE
                    s.document_id = :document_id
                    AND s.title ILIKE :pattern
                ORDER BY s.order_index
                LIMIT :limit
            """)

            result = await self._db.execute(
                suggestion_query,
                {
                    "document_id": str(document_id),
                    "pattern": f"%{partial_query}%",
                    "limit": limit,
                },
            )

            rows = result.fetchall()
            return [row[0] for row in rows]

        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}", exc_info=True)
            return []

    async def search_by_page(
        self, document_id: UUID, page_number: int
    ) -> list[SearchResult]:
        """
        Get all sections from a specific page.

        Args:
            document_id: Document ID
            page_number: Page number to retrieve

        Returns:
            List of sections on that page
        """
        try:
            page_query = text("""
                SELECT
                    s.id,
                    s.title,
                    LEFT(s.content, 200) as snippet,
                    s.page_number,
                    1.0 as rank,
                    s.level
                FROM sections s
                WHERE
                    s.document_id = :document_id
                    AND s.page_number = :page_number
                ORDER BY s.order_index
            """)

            result = await self._db.execute(
                page_query,
                {"document_id": str(document_id), "page_number": page_number},
            )

            rows = result.fetchall()

            return [
                SearchResult(
                    section_id=UUID(row[0]),
                    document_id=document_id,
                    title=row[1],
                    snippet=row[2],
                    page_number=row[3],
                    rank=float(row[4]),
                    level=row[5],
                )
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Page search failed: {e}", exc_info=True)
            return []

    async def get_search_stats(self, document_id: UUID) -> dict:
        """
        Get search statistics for a document.

        Args:
            document_id: Document ID

        Returns:
            Dictionary with search statistics
        """
        try:
            stats_query = text("""
                SELECT
                    COUNT(*) as total_sections,
                    COUNT(DISTINCT page_number) as total_pages,
                    AVG(LENGTH(content)) as avg_content_length
                FROM sections
                WHERE document_id = :document_id
            """)

            result = await self._db.execute(
                stats_query, {"document_id": str(document_id)}
            )

            row = result.fetchone()

            return {
                "total_sections": row[0] if row else 0,
                "total_pages": row[1] if row else 0,
                "avg_content_length": float(row[2]) if row and row[2] else 0,
            }

        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}", exc_info=True)
            return {"total_sections": 0, "total_pages": 0, "avg_content_length": 0}
