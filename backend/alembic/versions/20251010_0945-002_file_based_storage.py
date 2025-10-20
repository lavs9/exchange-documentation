"""File-based storage schema

Revision ID: 002
Revises: 001
Create Date: 2025-10-10 09:45:00

Creates new minimal schema for file-based architecture:
- documents: High-level metadata only
- document_versions: Version tracking
- chapters: Metadata + search index (NO content - stored in files)

Keeps existing 'sections' table for gradual migration.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create new file-based storage tables.

    Note: Does NOT drop existing 'sections' table to allow gradual migration.
    """
    # Create documents table (metadata only)
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('active_version', sa.String(length=50), nullable=True),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        if_not_exists=True
    )

    # Create document_versions table
    op.create_table(
        'document_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('metadata_file_path', sa.String(length=500), nullable=True),
        sa.Column('upload_date', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('approved_by', sa.String(length=255), nullable=True),
        sa.Column('approved_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'version', name='uq_document_version'),
        sa.CheckConstraint("status IN ('draft', 'active', 'archived')", name='ck_version_status'),
        if_not_exists=True
    )

    # Create chapters table (metadata + search index, NO content column)
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('version_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('page_range', sa.String(length=50), nullable=True),
        sa.Column('word_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('has_manual_content', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('has_linked_docs', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['document_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_id', 'chapter_number', name='uq_version_chapter'),
        if_not_exists=True
    )

    # Create indexes for performance
    op.create_index('idx_documents_slug', 'documents', ['slug'], unique=True, if_not_exists=True)
    op.create_index('idx_versions_document_id', 'document_versions', ['document_id'], if_not_exists=True)
    op.create_index('idx_versions_status', 'document_versions', ['status'], if_not_exists=True)
    op.create_index('idx_chapters_version_id', 'chapters', ['version_id'], if_not_exists=True)

    # Create GIN index for full-text search
    op.create_index(
        'idx_chapters_search',
        'chapters',
        ['search_vector'],
        postgresql_using='gin',
        if_not_exists=True
    )


def downgrade() -> None:
    """
    Drop file-based storage tables.

    Note: Does NOT affect existing 'sections' table.
    """
    # Drop indexes
    op.drop_index('idx_chapters_search', table_name='chapters', if_exists=True)
    op.drop_index('idx_chapters_version_id', table_name='chapters', if_exists=True)
    op.drop_index('idx_versions_status', table_name='document_versions', if_exists=True)
    op.drop_index('idx_versions_document_id', table_name='document_versions', if_exists=True)
    op.drop_index('idx_documents_slug', table_name='documents', if_exists=True)

    # Drop tables in reverse dependency order
    op.drop_table('chapters', if_exists=True)
    op.drop_table('document_versions', if_exists=True)
    op.drop_table('documents', if_exists=True)
