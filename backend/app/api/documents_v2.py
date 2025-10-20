"""
API endpoints for document management (file-based storage version).

This version reads chapter content from files instead of database.
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models import Document, DocumentVersion, Chapter
from app.schemas.document import (
    DocumentList,
    DocumentResponse,
    ProcessingStatus,
    TableOfContents,
    TOCEntry,
)
from app.services.file_storage import FileStorageService, FileStorageError
from app.services.document_processor_v2 import DocumentProcessor, DocumentProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload document (JSON, Markdown, or PDF)",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file"),
    file_type: str = Form(..., description="File type: 'json', 'markdown', or 'pdf'"),
    title: str = Form(..., description="Document title"),
    version: str = Form(..., description="Document version (e.g., 'v6.3')"),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """
    Upload document for processing with file-based storage.

    **File Types:**
    - **json**: Docling JSON (generates chapter-based structure)
    - **markdown**: Pre-processed markdown
    - **pdf**: PDF with companion Docling files

    **Processing Flow:**
    1. Creates document record
    2. Saves temp file
    3. Queues background processing
    4. Returns immediately

    Background processing:
    - Parses file into chapters
    - Saves chapters to files
    - Creates chapter metadata in DB
    - Generates search indexes
    """
    # Validate file_type
    valid_types = ["json", "markdown", "pdf"]
    if file_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file_type. Must be one of: {', '.join(valid_types)}",
        )

    # Validate file extension
    filename = file.filename or ""
    extension_map = {
        "json": [".json"],
        "markdown": [".md", ".markdown"],
        "pdf": [".pdf"],
    }
    expected_extensions = extension_map.get(file_type, [])
    if not any(filename.endswith(ext) for ext in expected_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension doesn't match file_type '{file_type}'"
        )

    try:
        processor = DocumentProcessor(db)

        # Create document record and save temp file
        document = await processor.create_document_record(
            file,
            title,
            version,
            metadata={"file_type": file_type},
            file_type=file_type,  # type: ignore
        )

        # Get temp file path (saved in create_document_record)
        from pathlib import Path
        from app.core.config import settings
        slug = processor._slugify(title)
        extension = {
            "json": ".json",
            "markdown": ".md",
            "pdf": ".pdf"
        }.get(file_type, ".dat")
        temp_path = settings.upload_dir / f"{slug}-{version}{extension}"

        # Queue background processing
        background_tasks.add_task(
            processor.process_document_async,
            document.id,
            str(temp_path),
            version,
            file_type,
        )

        logger.info(f"Document {document.id} queued for processing")

        return DocumentResponse(
            id=document.id,
            title=document.title,
            version=version,  # Use provided version
            upload_date=document.created_at,
            file_path=document.storage_path,
            page_count=None,
            processing_status="processing",
            metadata={"file_type": file_type},
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

    except DocumentProcessingError as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )


@router.get(
    "",
    response_model=DocumentList,
    summary="List all documents",
)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> DocumentList:
    """Get paginated list of all documents."""
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1",
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100",
        )

    # Get total count
    count_result = await db.execute(select(func.count(Document.id)))
    total = count_result.scalar() or 0

    # Get paginated documents
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Document)
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    documents = result.scalars().all()

    doc_responses = []
    for doc in documents:
        # Get active version info
        version_str = doc.active_version or "unknown"

        doc_responses.append(
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                version=version_str,
                upload_date=doc.created_at,
                file_path=doc.storage_path,
                page_count=None,  # Not stored anymore
                processing_status="completed" if doc.active_version else "processing",
                metadata={},
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
        )

    return DocumentList(
        documents=doc_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Get specific document by ID."""
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    return DocumentResponse(
        id=document.id,
        title=document.title,
        version=document.active_version or "unknown",
        upload_date=document.created_at,
        file_path=document.storage_path,
        page_count=None,
        processing_status="completed" if document.active_version else "processing",
        metadata={},
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete document and all its chapters."""
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    # Delete from database (cascades to versions and chapters)
    await db.delete(document)
    await db.commit()

    # TODO: Delete files from storage
    # file_storage = FileStorageService()
    # for version in document.versions:
    #     file_storage.delete_version_directory(document.slug, version.version)

    logger.info(f"Deleted document: {document_id}")


@router.get(
    "/{document_id}/status",
    response_model=ProcessingStatus,
    summary="Get document processing status",
)
async def get_document_status(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProcessingStatus:
    """Check processing status of a document."""
    try:
        processor = DocumentProcessor(db)
        return await processor.get_processing_status(document_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{document_id}/toc",
    response_model=TableOfContents,
    summary="Get table of contents",
)
async def get_table_of_contents(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TableOfContents:
    """Get hierarchical table of contents."""
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    # Get active version
    if not document.active_version:
        return TableOfContents(document_id=document_id, entries=[])

    result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version == document.active_version
        )
    )
    version = result.scalar_one_or_none()
    if not version:
        return TableOfContents(document_id=document_id, entries=[])

    # Get chapters
    result = await db.execute(
        select(Chapter)
        .where(Chapter.version_id == version.id)
        .order_by(Chapter.chapter_number)
    )
    chapters = result.scalars().all()

    # Generate TOC entries
    entries = [
        TOCEntry(
            id=str(ch.id),
            level=1,  # Chapters are level 1
            title=ch.title,
            page_number=int(ch.page_range.split('-')[0]) if ch.page_range else None,
            children=[],
        )
        for ch in chapters
    ]

    return TableOfContents(document_id=document_id, entries=entries)


@router.get(
    "/{document_id}/sections/{section_id}",
    response_model=dict,
    summary="Get a specific chapter",
)
async def get_section(
    document_id: UUID,
    section_id: UUID,
    include_backlinks: bool = True,
    resolve_links: bool = True,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get specific chapter content (reads from file).

    Args:
        document_id: Document UUID
        section_id: Chapter UUID
        include_backlinks: Include backlinks (who links here)
        resolve_links: Resolve [[wikilinks]] to URLs

    Returns:
        Chapter data with content read from file, optionally with backlinks
    """
    # Verify document exists
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    # Get chapter metadata
    chapter = await db.get(Chapter, section_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter not found: {section_id}",
        )

    # Verify chapter belongs to this document
    result = await db.execute(
        select(DocumentVersion.document_id).where(
            DocumentVersion.id == chapter.version_id
        )
    )
    chapter_doc_id = result.scalar_one_or_none()
    if chapter_doc_id != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter not found in this document",
        )

    # Use ChapterRenderService if backlinks or link resolution requested
    if include_backlinks or resolve_links:
        from app.services.chapter_render_service import ChapterRenderService

        render_service = ChapterRenderService()
        doc_path = f"storage/documents/{document.slug}/versions/{document.active_version}"

        try:
            rendered = render_service.render_chapter(
                chapter_file_path=chapter.file_path,
                doc_path=doc_path,
                include_backlinks=include_backlinks,
                resolve_links=resolve_links
            )

            content = rendered.content_with_resolved_links if resolve_links else rendered.content
            backlinks = rendered.backlinks if include_backlinks else []
            outline = rendered.outline
            metadata = rendered.metadata

        except Exception as e:
            logger.error(f"Failed to render chapter with links: {e}")
            # Fallback to basic read
            file_storage = FileStorageService()
            content = file_storage.read_chapter(chapter.file_path)
            backlinks = []
            outline = []
            metadata = {}
    else:
        # Basic read without link processing
        file_storage = FileStorageService()
        try:
            content = file_storage.read_chapter(chapter.file_path)
        except FileStorageError as e:
            logger.error(f"Failed to read chapter content: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read chapter content",
            )
        backlinks = []
        outline = []
        metadata = {}

    # Extract page number from page_range
    page_number = None
    if chapter.page_range:
        try:
            page_number = int(chapter.page_range.split('-')[0])
        except:
            pass

    response = {
        "id": str(chapter.id),
        "document_id": str(document_id),
        "level": 1,  # Chapters are level 1
        "title": chapter.title,
        "content": content,
        "page_number": page_number,
        "parent_id": None,
        "order_index": chapter.chapter_number,
        "file_path": chapter.file_path,  # Include file_path for wikilinks and backlinks
        "created_at": chapter.created_at.isoformat(),
        "updated_at": chapter.updated_at.isoformat(),
    }

    # Add optional fields if requested
    if include_backlinks:
        response["backlinks"] = backlinks
    if resolve_links or include_backlinks:
        response["outline"] = outline
        response["metadata"] = metadata

    return response


@router.put(
    "/{document_id}/sections/{section_id}",
    response_model=dict,
    summary="Update chapter content",
)
async def update_section_content(
    document_id: UUID,
    section_id: UUID,
    content: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Update chapter content (saves to file).

    Args:
        document_id: Document UUID
        section_id: Chapter UUID
        content: New markdown content

    Returns:
        Updated chapter data
    """
    # Verify document exists
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    # Get chapter
    chapter = await db.get(Chapter, section_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter not found: {section_id}",
        )

    # Write content to file
    file_storage = FileStorageService()
    try:
        # Read file path to extract info for re-saving
        from pathlib import Path
        path_parts = Path(chapter.file_path).parts
        # Reconstruct save call
        # file_path format: {doc-slug}/versions/{version}/chapters/chapter-XX-slug.md

        # Update content in file
        with open(file_storage._base_path / chapter.file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Update word count
        chapter.word_count = len(content.split())

        # Update search vector
        search_text = f"{chapter.title} {content}"
        await db.execute(
            Chapter.__table__.update()
            .where(Chapter.id == chapter.id)
            .values(search_vector=func.to_tsvector('english', search_text))
        )

        # Mark as manually edited
        chapter.has_manual_content = True

        await db.commit()
        await db.refresh(chapter)

        logger.info(f"Updated chapter {section_id}")

    except Exception as e:
        logger.error(f"Failed to update chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chapter content",
        )

    # Extract page number
    page_number = None
    if chapter.page_range:
        try:
            page_number = int(chapter.page_range.split('-')[0])
        except:
            pass

    return {
        "id": str(chapter.id),
        "document_id": str(document_id),
        "level": 1,
        "title": chapter.title,
        "content": content,
        "page_number": page_number,
        "parent_id": None,
        "order_index": chapter.chapter_number,
        "created_at": chapter.created_at.isoformat(),
        "updated_at": chapter.updated_at.isoformat(),
    }
