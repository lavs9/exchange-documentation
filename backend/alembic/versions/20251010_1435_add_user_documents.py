"""Add user_documents table for notes and references

Revision ID: 20251010_1435
Revises: 20251010_0945_002
Create Date: 2025-10-10 14:35:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.dialects.postgresql import TSVECTOR

# revision identifiers, used by Alembic.
revision = '20251010_1435'
down_revision = '20251010_0945_002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_documents table for notes and references."""

    # Create user_documents table
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            version VARCHAR(50) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            title TEXT NOT NULL,
            doc_type VARCHAR(20) NOT NULL CHECK (doc_type IN ('note', 'reference')),
            search_vector TSVECTOR,
            created_by VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            tags TEXT[]
        );
    """)

    # Create indexes
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_docs_search
        ON user_documents USING GIN(search_vector);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_docs_type
        ON user_documents(doc_type);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_docs_path
        ON user_documents(file_path);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_docs_document_id
        ON user_documents(document_id);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_docs_version
        ON user_documents(version);
    """)


def downgrade() -> None:
    """Drop user_documents table and indexes."""
    op.execute("DROP TABLE IF EXISTS user_documents CASCADE;")
