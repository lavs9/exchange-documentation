"""API endpoints for user-created documents (notes and references) and wikilinks."""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models import Document, UserDocument
from app.services.user_document_service import UserDocumentService, UserDocumentError
from app.services.wikilink_service import WikiLinkService
from app.services.file_storage import FileStorageService

logger = logging.getLogger(__name__)

router = APIRouter()


# =========================================================================
# Pydantic Schemas
# =========================================================================

class CreateUserDocumentRequest(BaseModel):
    """Request body for creating user document."""
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Markdown content")
    doc_type: str = Field(..., description="'note' or 'reference'")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags")
    link_to_source: Optional[str] = Field(
        default=None,
        description="Optional chapter file path to insert wikilink"
    )
    created_by: Optional[str] = Field(default=None, description="Username of creator")


class UpdateUserDocumentRequest(BaseModel):
    """Request body for updating user document."""
    content: str = Field(..., description="New markdown content")


class MoveUserDocumentRequest(BaseModel):
    """Request body for moving/renaming user document."""
    new_path: str = Field(..., description="New relative file path")


class UserDocumentResponse(BaseModel):
    """Response for user document."""
    id: str
    document_id: str
    version: str
    file_path: str
    title: str
    doc_type: str
    created_by: Optional[str]
    created_at: str
    updated_at: str
    tags: List[str]

    class Config:
        from_attributes = True


class UserDocumentWithContentResponse(UserDocumentResponse):
    """Response for user document with content and backlinks."""
    content: str
    backlinks: List[dict]


class BacklinkResponse(BaseModel):
    """Response for backlink."""
    source_file: str
    source_title: str
    snippet: str
    line_number: int


class GraphNodeResponse(BaseModel):
    """Response for graph node."""
    file_path: str
    file_type: str
    title: str
    links_to: List[str]
    linked_from: List[str]


class GraphResponse(BaseModel):
    """Response for link graph."""
    nodes: List[dict]
    edges: List[dict]


class LinkableDocumentResponse(BaseModel):
    """Response for linkable document (for autocomplete)."""
    filename: str
    title: str
    file_type: str


# =========================================================================
# Helper Functions
# =========================================================================

async def get_document_and_validate(
    document_id: UUID,
    version: str,
    db: AsyncSession
) -> tuple[Document, str]:
    """
    Get document and validate version, return document and slug.

    Raises HTTPException if document not found.
    """
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}"
        )

    return document, document.slug


# =========================================================================
# API Endpoints
# =========================================================================

@router.post(
    "/{document_id}/versions/{version}/notes",
    response_model=UserDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new note or reference"
)
async def create_note(
    document_id: UUID,
    version: str,
    request: CreateUserDocumentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new user document (note or reference).

    **Note Types:**
    - **note**: Personal annotation, explanation, or insight
    - **reference**: Guide, tutorial, or reference document

    **Optional Features:**
    - Set `link_to_source` to insert [[wikilink]] in source chapter
    - Add `tags` for categorization
    """
    try:
        document, doc_slug = await get_document_and_validate(document_id, version, db)

        service = UserDocumentService(db)

        user_doc = await service.create_document(
            document_id=document_id,
            doc_slug=doc_slug,
            version=version,
            title=request.title,
            content=request.content,
            doc_type=request.doc_type,
            created_by=request.created_by,
            tags=request.tags,
            link_to_source=request.link_to_source
        )

        return UserDocumentResponse(
            id=str(user_doc.id),
            document_id=str(user_doc.document_id),
            version=user_doc.version,
            file_path=user_doc.file_path,
            title=user_doc.title,
            doc_type=user_doc.doc_type,
            created_by=user_doc.created_by,
            created_at=user_doc.created_at.isoformat(),
            updated_at=user_doc.updated_at.isoformat(),
            tags=user_doc.tags or []
        )

    except UserDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{document_id}/versions/{version}/notes",
    response_model=List[UserDocumentResponse],
    summary="List notes and references"
)
async def list_notes(
    document_id: UUID,
    version: str,
    doc_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all user documents for a document version.

    **Query Parameters:**
    - `doc_type`: Optional filter by "note" or "reference"
    """
    try:
        await get_document_and_validate(document_id, version, db)

        service = UserDocumentService(db)
        documents = await service.list_documents(document_id, version, doc_type)

        return [
            UserDocumentResponse(
                id=str(doc.id),
                document_id=str(doc.document_id),
                version=doc.version,
                file_path=doc.file_path,
                title=doc.title,
                doc_type=doc.doc_type,
                created_by=doc.created_by,
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat(),
                tags=doc.tags or []
            )
            for doc in documents
        ]

    except UserDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{document_id}/versions/{version}/notes/{filename}",
    response_model=UserDocumentWithContentResponse,
    summary="Get note or reference with backlinks"
)
async def get_note(
    document_id: UUID,
    version: str,
    filename: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific user document with content and backlinks.

    Returns the document content along with all documents linking to it.
    """
    try:
        document, doc_slug = await get_document_and_validate(document_id, version, db)

        # Find user document by filename
        service = UserDocumentService(db)
        documents = await service.list_documents(document_id, version)

        user_doc = None
        for doc in documents:
            if filename in doc.file_path:
                user_doc = doc
                break

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User document not found: {filename}"
            )

        # Read content
        content = await service.read_document(user_doc.file_path)

        # Get backlinks
        wikilink_service = WikiLinkService()
        doc_path = f"storage/documents/{doc_slug}/versions/{version}"
        backlinks_data = wikilink_service.get_backlinks(
            target_file=user_doc.file_path,
            doc_path=doc_path
        )

        backlinks = [
            {
                "source_file": bl.source_file,
                "source_title": bl.source_title,
                "snippet": bl.snippet,
                "line_number": bl.line_number
            }
            for bl in backlinks_data
        ]

        return UserDocumentWithContentResponse(
            id=str(user_doc.id),
            document_id=str(user_doc.document_id),
            version=user_doc.version,
            file_path=user_doc.file_path,
            title=user_doc.title,
            doc_type=user_doc.doc_type,
            created_by=user_doc.created_by,
            created_at=user_doc.created_at.isoformat(),
            updated_at=user_doc.updated_at.isoformat(),
            tags=user_doc.tags or [],
            content=content,
            backlinks=backlinks
        )

    except UserDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{document_id}/versions/{version}/notes/{filename}",
    response_model=UserDocumentResponse,
    summary="Update note or reference content"
)
async def update_note(
    document_id: UUID,
    version: str,
    filename: str,
    request: UpdateUserDocumentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user document content.

    Regenerates search index automatically.
    """
    try:
        await get_document_and_validate(document_id, version, db)

        # Find user document by filename
        service = UserDocumentService(db)
        documents = await service.list_documents(document_id, version)

        user_doc = None
        for doc in documents:
            if filename in doc.file_path:
                user_doc = doc
                break

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User document not found: {filename}"
            )

        # Update document
        updated_doc = await service.update_document(user_doc.id, request.content)

        return UserDocumentResponse(
            id=str(updated_doc.id),
            document_id=str(updated_doc.document_id),
            version=updated_doc.version,
            file_path=updated_doc.file_path,
            title=updated_doc.title,
            doc_type=updated_doc.doc_type,
            created_by=updated_doc.created_by,
            created_at=updated_doc.created_at.isoformat(),
            updated_at=updated_doc.updated_at.isoformat(),
            tags=updated_doc.tags or []
        )

    except UserDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{document_id}/versions/{version}/notes/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note or reference"
)
async def delete_note(
    document_id: UUID,
    version: str,
    filename: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user document (file and database record).

    **Warning:** This does NOT remove wikilinks from other files.
    """
    try:
        await get_document_and_validate(document_id, version, db)

        # Find user document by filename
        service = UserDocumentService(db)
        documents = await service.list_documents(document_id, version)

        user_doc = None
        for doc in documents:
            if filename in doc.file_path:
                user_doc = doc
                break

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User document not found: {filename}"
            )

        # Delete document
        await service.delete_document(user_doc.id)

    except UserDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{document_id}/versions/{version}/notes/{filename}/move",
    response_model=UserDocumentResponse,
    summary="Move or rename note/reference"
)
async def move_note(
    document_id: UUID,
    version: str,
    filename: str,
    request: MoveUserDocumentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Move or rename user document.

    **Warning:** This does NOT update wikilinks in other files (manual task).
    """
    try:
        await get_document_and_validate(document_id, version, db)

        # Find user document by filename
        service = UserDocumentService(db)
        documents = await service.list_documents(document_id, version)

        user_doc = None
        for doc in documents:
            if filename in doc.file_path:
                user_doc = doc
                break

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User document not found: {filename}"
            )

        # Move document
        moved_doc = await service.move_document(user_doc.id, request.new_path)

        return UserDocumentResponse(
            id=str(moved_doc.id),
            document_id=str(moved_doc.document_id),
            version=moved_doc.version,
            file_path=moved_doc.file_path,
            title=moved_doc.title,
            doc_type=moved_doc.doc_type,
            created_by=moved_doc.created_by,
            created_at=moved_doc.created_at.isoformat(),
            updated_at=moved_doc.updated_at.isoformat(),
            tags=moved_doc.tags or []
        )

    except UserDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{document_id}/versions/{version}/backlinks/{filename}",
    response_model=List[BacklinkResponse],
    summary="Get backlinks to document"
)
async def get_backlinks(
    document_id: UUID,
    version: str,
    filename: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all documents linking to this file.

    Returns list of backlinks with context snippets.
    """
    try:
        document, doc_slug = await get_document_and_validate(document_id, version, db)

        # Construct file path
        # filename could be just "order-tips" or full path "notes/order-tips.md"
        if not filename.endswith('.md'):
            filename = filename + '.md'

        # Try to find in different directories
        possible_paths = [
            f"notes/{filename}",
            f"references/{filename}",
            f"chapters/{filename}",
            filename  # If already full path
        ]

        wikilink_service = WikiLinkService()
        doc_path = f"storage/documents/{doc_slug}/versions/{version}"

        backlinks = []
        for path in possible_paths:
            try:
                backlinks_data = wikilink_service.get_backlinks(
                    target_file=path,
                    doc_path=doc_path
                )
                if backlinks_data:
                    backlinks = [
                        BacklinkResponse(
                            source_file=bl.source_file,
                            source_title=bl.source_title,
                            snippet=bl.snippet,
                            line_number=bl.line_number
                        )
                        for bl in backlinks_data
                    ]
                    break
            except Exception:
                continue

        return backlinks

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get backlinks: {e}"
        )


@router.get(
    "/{document_id}/versions/{version}/graph",
    response_model=GraphResponse,
    summary="Get document link graph"
)
async def get_link_graph(
    document_id: UUID,
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete link graph for visualization.

    Returns nodes (documents) and edges (links between them).
    """
    try:
        document, doc_slug = await get_document_and_validate(document_id, version, db)

        wikilink_service = WikiLinkService()
        doc_path = f"storage/documents/{doc_slug}/versions/{version}"

        graph = wikilink_service.build_link_graph(doc_path)

        # Convert to nodes and edges format
        nodes = []
        edges = []

        for file_path, node in graph.items():
            nodes.append({
                "id": file_path,
                "file_path": node.file_path,
                "file_type": node.file_type,
                "title": node.title,
                "links_count": len(node.links_to),
                "backlinks_count": len(node.linked_from)
            })

            # Create edges for outgoing links
            for target in node.links_to:
                edges.append({
                    "source": file_path,
                    "target": target,
                    "type": "link"
                })

        return GraphResponse(nodes=nodes, edges=edges)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build link graph: {e}"
        )


@router.get(
    "/{document_id}/versions/{version}/search-linkable",
    response_model=List[LinkableDocumentResponse],
    summary="Get list of linkable documents for autocomplete"
)
async def get_linkable_documents(
    document_id: UUID,
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all linkable documents (for autocomplete in wikilink editor).

    Returns chapters, notes, and references.
    """
    try:
        document, doc_slug = await get_document_and_validate(document_id, version, db)

        file_storage = FileStorageService()
        doc_path = f"storage/documents/{doc_slug}/versions/{version}"
        base_path = file_storage._base_path / doc_slug / "versions" / version

        linkable = []

        # Get all markdown files
        for md_file in base_path.rglob("*.md"):
            try:
                rel_path = md_file.relative_to(base_path)
                filename = md_file.stem

                # Determine file type
                if str(rel_path).startswith("chapters"):
                    file_type = "chapter"
                elif str(rel_path).startswith("notes"):
                    file_type = "note"
                elif str(rel_path).startswith("references"):
                    file_type = "reference"
                else:
                    continue

                # Extract title from file
                content = md_file.read_text(encoding="utf-8")
                title = filename.replace('-', ' ').title()

                # Try to get better title from frontmatter or H1
                import re
                frontmatter_match = re.search(r'^---\s*\n.*?title:\s*["\']?(.+?)["\']?\s*\n.*?\n---', content, re.DOTALL)
                if frontmatter_match:
                    title = frontmatter_match.group(1).strip()
                else:
                    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    if h1_match:
                        title = h1_match.group(1).strip()

                linkable.append(LinkableDocumentResponse(
                    filename=filename,
                    title=title,
                    file_type=file_type
                ))

            except Exception as e:
                logger.warning(f"Error processing file {md_file}: {e}")
                continue

        # Sort by filename
        linkable.sort(key=lambda x: x.filename)

        return linkable

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get linkable documents: {e}"
        )
