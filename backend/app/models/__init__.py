"""Database models."""
# Import new file-based storage models
# Note: We use a separate model class but same table names
# This allows us to migrate gradually without duplicating tables

from app.models.document_v2 import Document
from app.models.version import DocumentVersion
from app.models.chapter import Chapter
from app.models.user_document import UserDocument

# Old models kept for reference during migration
# from app.models.document import Document as DocumentV1
# from app.models.section import Section

__all__ = [
    # New models (file-based)
    "Document",
    "DocumentVersion",
    "Chapter",
    "UserDocument",
]
