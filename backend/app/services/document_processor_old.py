"""Document processing service for PDF upload and processing."""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.database import engine
from app.models.document import Document
from app.models.section import Section
from app.schemas.document import ProcessingStatus
from app.services.docling_json_parser import DoclingJSONParser, DoclingParsingError
from app.services.rich_markdown_generator import generate_rich_markdown_from_json
from app.services.toc_generator import TOCGenerator

logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Raised when document processing fails."""

    pass


class DocumentProcessor:
    """Orchestrates PDF to structured document conversion."""

    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initialize document processor.

        Args:
            db_session: Database session
        """
        self._db = db_session
        self._parser = DoclingJSONParser()
        self._toc_generator = TOCGenerator()

    async def create_document_record(
        self,
        file: UploadFile,
        title: str,
        version: str,
        metadata: Optional[Dict] = None,
        file_type: Literal["pdf", "json", "markdown"] = "pdf",
    ) -> Document:
        """
        Create document record and save file (without processing).

        This method:
        1. Saves file to disk
        2. Creates database record with 'processing' status
        3. Returns immediately

        Processing happens asynchronously via process_document_async().

        Args:
            file: Uploaded file (PDF, JSON, or Markdown)
            title: Document title
            version: Document version
            metadata: Optional metadata dictionary
            file_type: Type of file ("pdf", "json", or "markdown")

        Returns:
            Created Document instance with 'processing' status

        Raises:
            DocumentProcessingError: If file save or DB insert fails
        """
        try:
            # Step 1: Save file to disk
            file_path = await self._save_file(file, title, version, file_type)

            # Step 2: Create document record with 'processing' status
            document = Document(
                title=title,
                version=version,
                file_path=str(file_path),
                processing_status="processing",
                metadata_=metadata or {"file_type": file_type},
            )
            self._db.add(document)
            await self._db.commit()
            await self._db.refresh(document)

            logger.info(f"Created document record: {document.id} (type: {file_type})")
            return document

        except Exception as e:
            logger.error(f"Failed to create document record: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to create document: {str(e)}") from e

    async def process_document_async(
        self,
        document_id: UUID,
        file_path: str,
    ) -> None:
        """
        Process document asynchronously in background.

        This method runs in a BackgroundTask and:
        1. Parses PDF with Docling
        2. Extracts sections
        3. Saves sections to database
        4. Updates document status to 'completed' or 'failed'

        Args:
            document_id: Document ID to process
            file_path: Path to PDF file

        Note: This method creates its own database session and handles
        all errors internally by updating document status.
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

                # Step 1: Determine file type and parse accordingly
                file_type = document.metadata_.get("file_type", "pdf") if document.metadata_ else "pdf"
                file_path_obj = Path(file_path)

                if file_type == "json":
                    # Use RichMarkdownGenerator for JSON files (chapter-based)
                    logger.info(f"Processing Docling JSON file: {file_path}")
                    with open(file_path_obj, "r", encoding="utf-8") as f:
                        docling_json = json.load(f)

                    chapters = generate_rich_markdown_from_json(docling_json)
                    logger.info(f"Generated {len(chapters)} chapters from JSON")

                    # Convert chapters to ParsedSection format
                    # Store FULL markdown_content in content field (for viewing)
                    # PostgreSQL FTS will index it automatically via search_vector
                    parsed_sections = []
                    for chapter in chapters:
                        from app.services.docling_json_parser import ParsedSection
                        parsed_sections.append(
                            ParsedSection(
                                level=1,  # Chapters are level 1
                                title=chapter.title,
                                content=chapter.markdown_content,  # Full markdown for viewing
                                page_number=chapter.page_range[0],
                                order_index=chapter.chapter_number,  # Use chapter number as order
                            )
                        )
                    page_count = max(ch.page_range[1] for ch in chapters)

                elif file_type == "markdown":
                    # Use DoclingJSONParser for markdown files
                    logger.info(f"Processing markdown file: {file_path}")
                    parser = DoclingJSONParser()
                    parsed_sections, page_count = parser.parse_markdown(file_path_obj)

                else:
                    # Legacy: Try to find companion files for PDF
                    parser = DoclingJSONParser()
                    md_path = file_path_obj.with_suffix(".md")
                    json_path = file_path_obj.with_suffix(".json")

                    if md_path.exists():
                        logger.info(f"Found Docling markdown: {md_path}")
                        parsed_sections, page_count = parser.parse_markdown(md_path)
                    elif json_path.exists():
                        logger.info(f"Found Docling JSON: {json_path}")
                        parsed_sections, page_count = parser.parse_json(json_path)
                    else:
                        raise DoclingParsingError(
                            f"No Docling output found. Expected {md_path} or {json_path}"
                        )

                logger.info(f"Parsed {len(parsed_sections)} sections, {page_count} pages")

                # Update page count
                document.page_count = page_count
                await db.commit()

                # Step 2: Save sections to database
                await self._save_sections_in_session(db, document_id, parsed_sections)

                # Step 3: Update status to completed
                document.processing_status = "completed"
                await db.commit()

                logger.info(f"Document processing completed: {document_id}")

            except DoclingParsingError as e:
                logger.error(f"Docling parsing failed for {document_id}: {e}", exc_info=True)
                await self._mark_as_failed(db, document_id)

            except Exception as e:
                logger.error(f"Document processing failed for {document_id}: {e}", exc_info=True)
                await self._mark_as_failed(db, document_id)

    async def _mark_as_failed(self, db: AsyncSession, document_id: UUID) -> None:
        """Mark document as failed."""
        try:
            document = await db.get(Document, document_id)
            if document:
                document.processing_status = "failed"
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to mark document as failed: {e}")


    async def get_processing_status(self, document_id: UUID) -> ProcessingStatus:
        """
        Get processing status of a document.

        Args:
            document_id: Document ID

        Returns:
            ProcessingStatus with current status
        """
        document = await self._db.get(Document, document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")

        return ProcessingStatus(
            document_id=document.id,
            status=document.processing_status,
            progress=100 if document.processing_status == "completed" else None,
        )

    async def _save_file(
        self,
        file: UploadFile,
        title: str,
        version: str,
        file_type: Literal["pdf", "json", "markdown"] = "pdf",
    ) -> Path:
        """
        Save uploaded file to disk with sanitized filename.

        Args:
            file: Uploaded file
            title: Document title (for filename)
            version: Document version (for filename)
            file_type: Type of file to determine extension

        Returns:
            Path to saved file

        Raises:
            DocumentProcessingError: If file save fails
        """
        try:
            # Ensure upload directory exists
            settings.upload_dir.mkdir(parents=True, exist_ok=True)

            # Generate safe filename
            safe_title = self._sanitize_filename(title)
            safe_version = self._sanitize_filename(version)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Determine file extension
            extension_map = {
                "pdf": ".pdf",
                "json": ".json",
                "markdown": ".md",
            }
            extension = extension_map.get(file_type, ".pdf")

            filename = f"{safe_title}_{safe_version}_{timestamp}{extension}"
            file_path = settings.upload_dir / filename

            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(f"Saved {file_type} file to: {file_path} ({len(content)} bytes)")
            return file_path

        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to save file: {str(e)}") from e

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize string for use in filename.

        Args:
            name: Original name

        Returns:
            Sanitized name safe for filesystem
        """
        import re

        # Replace spaces and special chars with underscores
        safe_name = re.sub(r"[^\w\-.]", "_", name)
        # Remove consecutive underscores
        safe_name = re.sub(r"_+", "_", safe_name)
        # Truncate to reasonable length
        return safe_name[:100]

    async def _save_sections(
        self, document_id: UUID, parsed_sections: List
    ) -> None:
        """
        Save parsed sections to database with hierarchy (uses self._db).

        Args:
            document_id: Parent document ID
            parsed_sections: List of ParsedSection objects from parser

        Raises:
            DocumentProcessingError: If saving fails
        """
        await self._save_sections_in_session(self._db, document_id, parsed_sections)

    async def _save_sections_in_session(
        self, db: AsyncSession, document_id: UUID, parsed_sections: List
    ) -> None:
        """
        Save parsed sections to database with hierarchy using provided session.

        Args:
            db: Database session to use
            document_id: Parent document ID
            parsed_sections: List of ParsedSection objects from parser

        Raises:
            DocumentProcessingError: If saving fails
        """
        try:
            # Map to track section IDs for parent relationships
            section_map: Dict[int, UUID] = {}  # order_index -> section_id
            parent_stack: List[tuple[int, UUID]] = []  # (level, section_id)

            for parsed in parsed_sections:
                # Determine parent based on level
                parent_id = None

                # Pop stack until we find a parent with lower level
                while parent_stack and parent_stack[-1][0] >= parsed.level:
                    parent_stack.pop()

                if parent_stack:
                    parent_id = parent_stack[-1][1]

                # Create section record
                section = Section(
                    id=uuid4(),
                    document_id=document_id,
                    level=parsed.level,
                    title=parsed.title,
                    content=parsed.content,
                    page_number=parsed.page_number,
                    parent_id=parent_id,
                    order_index=parsed.order_index,
                )

                db.add(section)

                # Track for parent relationships
                section_map[parsed.order_index] = section.id
                parent_stack.append((parsed.level, section.id))

            # Commit all sections
            await db.commit()

            logger.info(
                f"Saved {len(parsed_sections)} sections for document {document_id}"
            )

        except Exception as e:
            logger.error(f"Failed to save sections: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to save sections: {str(e)}") from e
