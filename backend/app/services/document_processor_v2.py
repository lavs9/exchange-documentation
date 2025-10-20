"""
Document processing service for file-based storage architecture.

This version uses FileStorageService to store content in files and only
metadata in the database.
"""
import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.core.config import settings
from app.core.database import engine
from app.models import Document, DocumentVersion, Chapter
from app.schemas.document import ProcessingStatus
from app.services.file_storage import FileStorageService, FileStorageError
from app.services.rich_markdown_generator import generate_rich_markdown_from_json
from app.services.docling_json_parser import DoclingJSONParser, DoclingParsingError

logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Raised when document processing fails."""
    pass


class DocumentProcessor:
    """Orchestrates document conversion with file-based storage."""

    def __init__(
        self,
        db_session: AsyncSession,
        file_storage: Optional[FileStorageService] = None
    ) -> None:
        """
        Initialize document processor.

        Args:
            db_session: Database session
            file_storage: File storage service (defaults to standard location)
        """
        self._db = db_session
        self._file_storage = file_storage or FileStorageService()
        self._parser = DoclingJSONParser()

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        text = text.lower()
        text = re.sub(r'[\s_]+', '-', text)
        text = re.sub(r'[^a-z0-9-]', '', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')[:50]

    async def create_document_record(
        self,
        file: UploadFile,
        title: str,
        version: str,
        metadata: Optional[Dict] = None,
        file_type: Literal["pdf", "json", "markdown"] = "json",
    ) -> Document:
        """
        Create document record and save file (without processing).

        Args:
            file: Uploaded file
            title: Document title
            version: Version string (e.g., "v6.3")
            metadata: Optional metadata
            file_type: Type of file

        Returns:
            Created Document instance

        Raises:
            DocumentProcessingError: If creation fails
        """
        try:
            # Generate slug from title
            slug = self._slugify(title)

            # Check if document exists
            result = await self._db.execute(
                select(Document).where(Document.slug == slug)
            )
            document = result.scalar_one_or_none()

            if not document:
                # Create new document
                storage_path = f"{slug}"
                document = Document(
                    slug=slug,
                    title=title,
                    active_version=None,  # Will be set after processing
                    storage_path=storage_path,
                )
                self._db.add(document)
                await self._db.commit()
                await self._db.refresh(document)
                logger.info(f"Created document: {document.id} (slug: {slug})")
            else:
                logger.info(f"Using existing document: {document.id} (slug: {slug})")

            # Save uploaded file temporarily
            temp_path = await self._save_temp_file(file, slug, version, file_type)

            logger.info(f"Document record ready: {document.id}")
            return document

        except Exception as e:
            logger.error(f"Failed to create document record: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to create document: {str(e)}") from e

    async def _save_temp_file(
        self,
        file: UploadFile,
        slug: str,
        version: str,
        file_type: str
    ) -> Path:
        """Save uploaded file temporarily for processing."""
        upload_dir = settings.upload_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        extension = {
            "json": ".json",
            "markdown": ".md",
            "pdf": ".pdf"
        }.get(file_type, ".dat")

        temp_filename = f"{slug}-{version}{extension}"
        temp_path = upload_dir / temp_filename

        # Save file
        content = await file.read()
        temp_path.write_bytes(content)

        logger.info(f"Saved temp file: {temp_path}")
        return temp_path

    async def process_document_async(
        self,
        document_id: UUID,
        temp_file_path: str,
        version: str,
        file_type: str = "json"
    ) -> None:
        """
        Process document asynchronously in background.

        This method:
        1. Parses the file and generates chapters
        2. Saves each chapter to file system
        3. Creates chapter records in database (metadata only)
        4. Generates search indexes
        5. Sets version as active

        Args:
            document_id: Document ID
            temp_file_path: Path to temporary uploaded file
            version: Version string
            file_type: Type of file
        """
        # Create new database session for background task
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as db:
            try:
                logger.info(f"Starting background processing for document {document_id}")

                # Get document
                document = await db.get(Document, document_id)
                if not document:
                    logger.error(f"Document not found: {document_id}")
                    return

                # Step 1: Parse file and generate chapters
                temp_path = Path(temp_file_path)
                chapters_data = await self._parse_file(temp_path, file_type)

                logger.info(f"Generated {len(chapters_data)} chapters")

                # Step 2: Create or get document version
                result = await db.execute(
                    select(DocumentVersion).where(
                        DocumentVersion.document_id == document_id,
                        DocumentVersion.version == version
                    )
                )
                doc_version = result.scalar_one_or_none()

                if not doc_version:
                    doc_version = DocumentVersion(
                        document_id=document_id,
                        version=version,
                        status="active",
                    )
                    db.add(doc_version)
                    await db.commit()
                    await db.refresh(doc_version)
                    logger.info(f"Created document version: {doc_version.id}")

                # Step 3: Save chapters to file system and create DB records
                for chapter_data in chapters_data:
                    # Save chapter content to file
                    file_path = self._file_storage.save_chapter(
                        doc_slug=document.slug,
                        version=version,
                        chapter_number=chapter_data["chapter_number"],
                        title=chapter_data["title"],
                        content=chapter_data["content"],
                    )

                    # Calculate word count
                    word_count = len(chapter_data["content"].split())

                    # Generate search vector
                    search_text = f"{chapter_data['title']} {chapter_data['content']}"

                    # Create chapter record (metadata only)
                    chapter = Chapter(
                        version_id=doc_version.id,
                        chapter_number=chapter_data["chapter_number"],
                        title=chapter_data["title"],
                        file_path=file_path,
                        page_range=chapter_data.get("page_range"),
                        word_count=word_count,
                        has_manual_content=False,
                        has_linked_docs=False,
                    )
                    db.add(chapter)
                    await db.flush()

                    # Generate PostgreSQL full-text search vector
                    await db.execute(
                        Chapter.__table__.update()
                        .where(Chapter.id == chapter.id)
                        .values(search_vector=func.to_tsvector('english', search_text))
                    )

                await db.commit()
                logger.info(f"Saved {len(chapters_data)} chapters to file system")

                # Step 4: Save metadata
                metadata = {
                    "version": version,
                    "file_type": file_type,
                    "chapter_count": len(chapters_data),
                    "processed_at": datetime.utcnow().isoformat(),
                }
                self._file_storage.save_metadata(document.slug, version, metadata)

                # Step 5: Set as active version
                document.active_version = version
                self._file_storage.set_active_version(document.slug, version)
                await db.commit()

                logger.info(f"Document {document_id} processing completed successfully")

                # Clean up temp file
                temp_path.unlink(missing_ok=True)

            except Exception as e:
                logger.error(
                    f"Document processing failed for {document_id}: {e}",
                    exc_info=True
                )
                # Update status to failed if possible
                try:
                    doc_version.status = "draft"  # Mark as draft instead of active
                    await db.commit()
                except:
                    pass

    async def _parse_file(
        self,
        file_path: Path,
        file_type: str
    ) -> List[Dict]:
        """
        Parse file and return chapter data.

        Returns:
            List of chapter dictionaries with:
            - chapter_number: int
            - title: str
            - content: str (markdown)
            - page_range: str (optional)
        """
        if file_type == "json":
            # Use RichMarkdownGenerator for JSON files
            with open(file_path, "r", encoding="utf-8") as f:
                docling_json = json.load(f)

            chapters = generate_rich_markdown_from_json(docling_json)

            return [
                {
                    "chapter_number": ch.chapter_number,
                    "title": ch.title,
                    "content": ch.markdown_content,
                    "page_range": f"{ch.page_range[0]}-{ch.page_range[1]}",
                }
                for ch in chapters
            ]

        elif file_type == "markdown":
            # Parse markdown file
            parsed_sections, page_count = self._parser.parse_markdown(file_path)

            # Group sections into chapters (level 1 headings)
            chapters = []
            current_chapter = None
            chapter_num = 0

            for section in parsed_sections:
                if section.level == 1:
                    # New chapter
                    if current_chapter:
                        chapters.append(current_chapter)

                    chapter_num += 1
                    current_chapter = {
                        "chapter_number": chapter_num,
                        "title": section.title,
                        "content": section.content,
                        "page_range": f"{section.page_number}",
                    }
                elif current_chapter:
                    # Add subsection to current chapter
                    current_chapter["content"] += f"\n\n{section.content}"

            if current_chapter:
                chapters.append(current_chapter)

            return chapters

        else:
            raise DocumentProcessingError(f"Unsupported file type: {file_type}")

    async def get_processing_status(self, document_id: UUID) -> ProcessingStatus:
        """
        Get processing status for a document.

        Args:
            document_id: Document ID

        Returns:
            Processing status information
        """
        document = await self._db.get(Document, document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")

        # Check if active version exists
        if document.active_version:
            # Get version info
            result = await self._db.execute(
                select(DocumentVersion).where(
                    DocumentVersion.document_id == document_id,
                    DocumentVersion.version == document.active_version
                )
            )
            version = result.scalar_one_or_none()

            if version:
                # Count chapters
                result = await self._db.execute(
                    select(func.count(Chapter.id)).where(
                        Chapter.version_id == version.id
                    )
                )
                chapter_count = result.scalar()

                return ProcessingStatus(
                    document_id=str(document_id),
                    status="completed",
                    progress=100,
                    message=f"Processing complete - {chapter_count} chapters",
                    error_message=None,
                )

        # Still processing
        return ProcessingStatus(
            document_id=str(document_id),
            status="processing",
            progress=50,
            message="Processing document...",
            error_message=None,
        )
