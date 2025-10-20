"""Service for managing user-created documents (notes and references)."""
import logging
import re
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserDocument, Document, Chapter
from app.services.file_storage import FileStorageService, FileStorageError

logger = logging.getLogger(__name__)


class UserDocumentError(Exception):
    """Base exception for user document operations."""
    pass


class UserDocumentService:
    """
    Service for managing user-created notes and references.

    Provides CRUD operations for user documents with file-based storage
    and database metadata/search indexing.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        file_storage: Optional[FileStorageService] = None
    ):
        """
        Initialize UserDocumentService.

        Args:
            db_session: Database session
            file_storage: File storage service (creates default if not provided)
        """
        self._db = db_session
        self._file_storage = file_storage or FileStorageService()

    async def create_document(
        self,
        document_id: UUID,
        doc_slug: str,
        version: str,
        title: str,
        content: str,
        doc_type: str,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        link_to_source: Optional[str] = None,
    ) -> UserDocument:
        """
        Create new user document (note or reference).

        Args:
            document_id: Parent document ID
            doc_slug: Document slug
            version: Document version
            title: Note/reference title
            content: Markdown content
            doc_type: "note" or "reference"
            created_by: Username of creator
            tags: Optional list of tags
            link_to_source: Optional chapter file path to insert wikilink

        Returns:
            Created UserDocument

        Raises:
            UserDocumentError: If creation fails
        """
        try:
            # Validate doc_type
            if doc_type not in ["note", "reference"]:
                raise UserDocumentError(f"Invalid doc_type: {doc_type}. Must be 'note' or 'reference'")

            # Generate filename from title
            filename = self._slugify(title) + ".md"
            directory = "notes" if doc_type == "note" else "references"

            # Save to file
            file_path = self._file_storage.save_user_document(
                doc_slug=doc_slug,
                version=version,
                directory=directory,
                filename=filename,
                content=content
            )

            # Insert wikilink in source chapter if requested
            if link_to_source:
                await self._insert_wikilink_in_chapter(
                    doc_slug=doc_slug,
                    version=version,
                    chapter_file_path=link_to_source,
                    target_filename=Path(filename).stem
                )

            # Create DB record
            user_doc = UserDocument(
                document_id=document_id,
                version=version,
                file_path=file_path,
                title=title,
                doc_type=doc_type,
                created_by=created_by,
                tags=tags or []
            )

            self._db.add(user_doc)
            await self._db.flush()

            # Generate search vector
            search_text = f"{title} {content}"
            await self._db.execute(
                text("""
                    UPDATE user_documents
                    SET search_vector = to_tsvector('english', :search_text)
                    WHERE id = :doc_id
                """),
                {"search_text": search_text, "doc_id": str(user_doc.id)}
            )

            await self._db.commit()

            logger.info(f"Created user document: {title} ({doc_type})")
            return user_doc

        except FileStorageError as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to save document file: {e}") from e
        except Exception as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to create user document: {e}") from e

    async def read_document(self, file_path: str) -> str:
        """
        Read user document content from file.

        Args:
            file_path: Relative file path

        Returns:
            Markdown content

        Raises:
            UserDocumentError: If read fails
        """
        try:
            return self._file_storage.read_user_document(file_path)
        except FileStorageError as e:
            raise UserDocumentError(f"Failed to read document: {e}") from e

    async def update_document(
        self,
        user_doc_id: UUID,
        content: str
    ) -> UserDocument:
        """
        Update user document content.

        Args:
            user_doc_id: User document ID
            content: New markdown content

        Returns:
            Updated UserDocument

        Raises:
            UserDocumentError: If update fails
        """
        try:
            # Get user document
            user_doc = await self._db.get(UserDocument, user_doc_id)
            if not user_doc:
                raise UserDocumentError(f"User document not found: {user_doc_id}")

            # Update file
            self._file_storage.update_user_document(user_doc.file_path, content)

            # Regenerate search vector
            search_text = f"{user_doc.title} {content}"
            await self._db.execute(
                text("""
                    UPDATE user_documents
                    SET search_vector = to_tsvector('english', :search_text),
                        updated_at = NOW()
                    WHERE id = :doc_id
                """),
                {"search_text": search_text, "doc_id": str(user_doc_id)}
            )

            await self._db.commit()
            await self._db.refresh(user_doc)

            logger.info(f"Updated user document: {user_doc.title}")
            return user_doc

        except FileStorageError as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to update document file: {e}") from e
        except Exception as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to update user document: {e}") from e

    async def list_documents(
        self,
        document_id: UUID,
        version: str,
        doc_type: Optional[str] = None
    ) -> List[UserDocument]:
        """
        List user documents for a document version.

        Args:
            document_id: Parent document ID
            version: Document version
            doc_type: Optional filter by "note" or "reference"

        Returns:
            List of UserDocuments

        Raises:
            UserDocumentError: If query fails
        """
        try:
            query = select(UserDocument).where(
                UserDocument.document_id == document_id,
                UserDocument.version == version
            )

            if doc_type:
                query = query.where(UserDocument.doc_type == doc_type)

            query = query.order_by(UserDocument.created_at.desc())

            result = await self._db.execute(query)
            documents = result.scalars().all()

            logger.debug(f"Found {len(documents)} user documents for {document_id}/{version}")
            return list(documents)

        except Exception as e:
            raise UserDocumentError(f"Failed to list user documents: {e}") from e

    async def delete_document(self, user_doc_id: UUID) -> None:
        """
        Delete user document (file and DB record).

        Args:
            user_doc_id: User document ID

        Raises:
            UserDocumentError: If deletion fails
        """
        try:
            # Get user document
            user_doc = await self._db.get(UserDocument, user_doc_id)
            if not user_doc:
                raise UserDocumentError(f"User document not found: {user_doc_id}")

            # Delete file
            self._file_storage.delete_user_document(user_doc.file_path)

            # Delete DB record
            await self._db.delete(user_doc)
            await self._db.commit()

            logger.info(f"Deleted user document: {user_doc.title}")

        except FileStorageError as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to delete document file: {e}") from e
        except Exception as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to delete user document: {e}") from e

    async def move_document(
        self,
        user_doc_id: UUID,
        new_path: str
    ) -> UserDocument:
        """
        Move/rename user document.

        Note: This does NOT update wikilinks in other files (manual task).

        Args:
            user_doc_id: User document ID
            new_path: New relative file path

        Returns:
            Updated UserDocument

        Raises:
            UserDocumentError: If move fails
        """
        try:
            # Get user document
            user_doc = await self._db.get(UserDocument, user_doc_id)
            if not user_doc:
                raise UserDocumentError(f"User document not found: {user_doc_id}")

            old_path = user_doc.file_path

            # Move file
            self._file_storage.move_user_document(old_path, new_path)

            # Update DB
            user_doc.file_path = new_path
            await self._db.commit()
            await self._db.refresh(user_doc)

            logger.info(f"Moved user document from {old_path} to {new_path}")
            return user_doc

        except FileStorageError as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to move document file: {e}") from e
        except Exception as e:
            await self._db.rollback()
            raise UserDocumentError(f"Failed to move user document: {e}") from e

    async def search_documents(
        self,
        document_id: UUID,
        query: str,
        doc_type: Optional[str] = None,
        limit: int = 20
    ) -> List[dict]:
        """
        Full-text search user documents.

        Args:
            document_id: Parent document ID
            query: Search query
            doc_type: Optional filter by "note" or "reference"
            limit: Maximum results

        Returns:
            List of search results with relevance ranking

        Raises:
            UserDocumentError: If search fails
        """
        try:
            # Build search query
            sql = """
                SELECT
                    id,
                    title,
                    file_path,
                    doc_type,
                    created_at,
                    ts_rank(search_vector, plainto_tsquery('english', :query)) as rank
                FROM user_documents
                WHERE document_id = :document_id
                    AND search_vector @@ plainto_tsquery('english', :query)
            """

            params = {
                "document_id": str(document_id),
                "query": query,
                "limit": limit
            }

            if doc_type:
                sql += " AND doc_type = :doc_type"
                params["doc_type"] = doc_type

            sql += " ORDER BY rank DESC, created_at DESC LIMIT :limit"

            result = await self._db.execute(text(sql), params)
            rows = result.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": str(row.id),
                    "title": row.title,
                    "file_path": row.file_path,
                    "doc_type": row.doc_type,
                    "created_at": row.created_at.isoformat(),
                    "rank": float(row.rank)
                })

            logger.info(f"Found {len(results)} user documents matching '{query}'")
            return results

        except Exception as e:
            raise UserDocumentError(f"Failed to search user documents: {e}") from e

    async def _insert_wikilink_in_chapter(
        self,
        doc_slug: str,
        version: str,
        chapter_file_path: str,
        target_filename: str
    ) -> None:
        """
        Insert wikilink at end of chapter file.

        Args:
            doc_slug: Document slug
            version: Document version
            chapter_file_path: Chapter ID (UUID) or file path
            target_filename: Target filename (without .md)

        Raises:
            UserDocumentError: If insertion fails
        """
        try:
            # Check if chapter_file_path is a UUID (chapter ID)
            from uuid import UUID as check_UUID
            try:
                chapter_id = check_UUID(chapter_file_path)
                # It's a UUID, so we need to get the file path from DB
                from app.models import Chapter
                chapter = await self._db.get(Chapter, chapter_id)
                if not chapter:
                    raise UserDocumentError(f"Chapter not found: {chapter_file_path}")
                actual_file_path = chapter.file_path
            except (ValueError, AttributeError):
                # It's already a file path
                actual_file_path = chapter_file_path

            # Read current chapter content
            content = self._file_storage.read_chapter(actual_file_path)

            # Append wikilink
            wikilink = f"\n\n## Related Notes\n\n- [[{target_filename}]]\n"

            # Check if "Related Notes" section already exists
            if "## Related Notes" in content:
                # Append to existing section
                content = content.replace(
                    "## Related Notes",
                    f"## Related Notes\n\n- [[{target_filename}]]"
                )
            else:
                # Add new section at end
                content += wikilink

            # Write back to file
            full_path = self._file_storage._base_path / actual_file_path
            full_path.write_text(content, encoding="utf-8")

            logger.info(f"Inserted wikilink to {target_filename} in {actual_file_path}")

        except Exception as e:
            logger.error(f"Failed to insert wikilink: {e}")
            raise UserDocumentError(f"Failed to insert wikilink: {e}") from e

    def _slugify(self, text: str) -> str:
        """
        Convert text to filename-safe slug.

        Args:
            text: Text to slugify

        Returns:
            Slugified string (lowercase, hyphens, alphanumeric)
        """
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and underscores with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        # Remove non-alphanumeric characters (keep hyphens)
        text = re.sub(r'[^a-z0-9-]', '', text)
        # Remove duplicate hyphens
        text = re.sub(r'-+', '-', text)
        # Strip leading/trailing hyphens
        text = text.strip('-')
        # Limit length
        return text[:50]
