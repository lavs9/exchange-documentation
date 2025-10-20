"""API endpoints for document management."""
import logging
from typing import Optional
from uuid import UUID

import aiofiles
from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, UploadFile, status
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.dependencies import get_db
from app.models.document import Document
from app.models.section import Section
from app.schemas.document import (
    DocumentList,
    DocumentResponse,
    DocumentWithSections,
    ProcessingStatus,
    TableOfContents,
)
from app.services.document_processor import DocumentProcessor, DocumentProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload document (JSON, Markdown, or PDF with Docling output)",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file (JSON, Markdown, or PDF)"),
    file_type: str = Form(..., description="File type: 'json', 'markdown', or 'pdf'"),
    docling_json: Optional[UploadFile] = File(None, description="Docling JSON output (for PDF only)"),
    docling_md: Optional[UploadFile] = File(None, description="Docling Markdown output (for PDF only)"),
    title: str = Form(..., description="Document title"),
    version: str = Form(..., description="Document version (e.g., 'v6.2')"),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """
    Upload document for processing.

    **Supported Upload Types:**

    1. **JSON File** (Docling JSON):
       - file_type: "json"
       - Rich markdown with chapter-based organization
       - Generates ~12 chapter sections instead of 325 individual sections
       - Includes callouts, cross-references, and enhanced formatting

    2. **Markdown File** (Docling Markdown):
       - file_type: "markdown"
       - Pre-processed markdown from Docling
       - Standard section-based parsing

    3. **PDF File** (Legacy):
       - file_type: "pdf"
       - Requires companion docling_json or docling_md file
       - Standard section-based parsing

    **Chapter-Based Architecture (JSON files):**
    - ONE database section per chapter (not per heading)
    - Faster loading and better navigation
    - Rich markdown with YAML frontmatter, GFM tables, Obsidian callouts
    - Internal cross-references and page references

    This endpoint:
    1. Validates file type and extensions
    2. Saves file(s) to disk
    3. Creates document record with 'processing' status
    4. Queues background processing
    5. Returns immediately with document ID

    Use /documents/{document_id}/status to check processing progress.
    """
    # Validate file_type
    valid_types = ["json", "markdown", "pdf"]
    if file_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file_type. Must be one of: {', '.join(valid_types)}",
        )

    # Validate file extension matches file_type
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
            detail=f"File extension doesn't match file_type '{file_type}'. Expected: {', '.join(expected_extensions)}",
        )

    # For PDF files, validate that companion files are provided
    if file_type == "pdf" and not docling_json and not docling_md:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF upload requires either docling_json or docling_md companion file",
        )

    # Validate file sizes
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size = 52428800  # 50MB
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds 50MB limit",
        )

    try:
        processor = DocumentProcessor(db)

        # Create document record and save main file
        document = await processor.create_document_record(
            file,
            title,
            version,
            metadata={"file_type": file_type},
            file_type=file_type,  # type: ignore
        )

        # For PDF files, save companion Docling output files
        if file_type == "pdf":
            base_path = Path(document.file_path)

            if docling_json:
                json_path = base_path.with_suffix(".json")
                async with aiofiles.open(json_path, "wb") as f:
                    content = await docling_json.read()
                    await f.write(content)
                logger.info(f"Saved Docling JSON: {json_path}")

            if docling_md:
                md_path = base_path.with_suffix(".md")
                async with aiofiles.open(md_path, "wb") as f:
                    content = await docling_md.read()
                    await f.write(content)
                logger.info(f"Saved Docling Markdown: {md_path}")

        # Queue background processing
        background_tasks.add_task(
            processor.process_document_async,
            document.id,
            document.file_path,
        )

        logger.info(f"Document {document.id} ({file_type}) queued for processing")
        return DocumentResponse.model_validate(document)

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
    """
    Get a paginated list of all documents.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)

    Returns:
        Paginated list of documents
    """
    # Validate pagination
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
    count_result = await db.execute(select(Document))
    total = len(count_result.scalars().all())

    # Get paginated documents
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Document).order_by(Document.upload_date.desc()).offset(offset).limit(page_size)
    )
    documents = result.scalars().all()

    return DocumentList(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
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
    """
    Get a specific document by ID.

    Args:
        document_id: Document UUID

    Returns:
        Document details
    """
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    return DocumentResponse.model_validate(document)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a document and all its sections.

    Args:
        document_id: Document UUID
    """
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    await db.delete(document)
    await db.commit()

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
    """
    Check the processing status of a document.

    Args:
        document_id: Document UUID

    Returns:
        Processing status information
    """
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
    """
    Get the hierarchical table of contents for a document.

    Args:
        document_id: Document UUID

    Returns:
        Table of contents with nested structure
    """
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    # Get all sections for the document
    result = await db.execute(
        select(Section)
        .where(Section.document_id == document_id)
        .order_by(Section.order_index)
    )
    sections = result.scalars().all()

    # Generate TOC from sections
    from app.services.toc_generator import TOCGenerator
    toc_generator = TOCGenerator()
    toc_entries = toc_generator.generate_toc(list(sections))

    return TableOfContents(document_id=document_id, entries=toc_entries)

@router.get(
    "/{document_id}/sections/{section_id}",
    response_model=dict,
    summary="Get a specific section",
)
async def get_section(
    document_id: UUID,
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get a specific section by ID.

    Args:
        document_id: Document UUID
        section_id: Section UUID

    Returns:
        Section data with all fields
    """
    # Verify document exists
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    # Get section
    section = await db.get(Section, section_id)
    if not section or section.document_id != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section not found: {section_id}",
        )

    return {
        "id": str(section.id),
        "document_id": str(section.document_id),
        "level": section.level,
        "title": section.title,
        "content": section.content,
        "page_number": section.page_number,
        "parent_id": str(section.parent_id) if section.parent_id else None,
        "order_index": section.order_index,
        "created_at": section.created_at.isoformat(),
        "updated_at": section.updated_at.isoformat(),
    }


@router.put(
    "/{document_id}/sections/{section_id}",
    response_model=dict,
    summary="Update section content",
)
async def update_section_content(
    document_id: UUID,
    section_id: UUID,
    content: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Update the content of a specific section.

    Args:
        document_id: Document UUID
        section_id: Section UUID
        content: New markdown content for the section

    Returns:
        Updated section data
    """
    # Verify document exists
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    # Get section
    section = await db.get(Section, section_id)
    if not section or section.document_id != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section not found: {section_id}",
        )

    # Update content
    section.content = content
    await db.commit()
    await db.refresh(section)

    logger.info(f"Updated section {section_id} in document {document_id}")

    return {
        "id": str(section.id),
        "document_id": str(section.document_id),
        "level": section.level,
        "title": section.title,
        "content": section.content,
        "page_number": section.page_number,
        "parent_id": str(section.parent_id) if section.parent_id else None,
        "order_index": section.order_index,
        "created_at": section.created_at.isoformat(),
        "updated_at": section.updated_at.isoformat(),
    }
