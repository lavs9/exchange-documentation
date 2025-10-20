-- Migration to File-Based Storage Schema
-- This script creates the new schema while preserving existing data

-- Step 1: Rename old tables to backup (instead of dropping)
ALTER TABLE IF EXISTS documents RENAME TO documents_old;
ALTER TABLE IF EXISTS sections RENAME TO sections_old;

-- Step 2: Create new documents table (metadata only)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    active_version VARCHAR(50),
    storage_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Step 3: Create document_versions table
CREATE TABLE IF NOT EXISTS document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'active', 'archived')),
    metadata_file_path VARCHAR(500),
    upload_date TIMESTAMP DEFAULT NOW(),
    approved_by VARCHAR(255),
    approved_at TIMESTAMP,
    UNIQUE(document_id, version)
);

-- Step 4: Create chapters table (metadata + search index, NO content)
CREATE TABLE IF NOT EXISTS chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id UUID REFERENCES document_versions(id) ON DELETE CASCADE,
    chapter_number INT NOT NULL,
    title TEXT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    page_range VARCHAR(50),
    word_count INT DEFAULT 0,
    has_manual_content BOOLEAN DEFAULT FALSE,
    has_linked_docs BOOLEAN DEFAULT FALSE,
    search_vector TSVECTOR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(version_id, chapter_number)
);

-- Step 5: Create indexes
CREATE INDEX IF NOT EXISTS idx_documents_slug ON documents(slug);
CREATE INDEX IF NOT EXISTS idx_versions_document_id ON document_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_versions_status ON document_versions(status);
CREATE INDEX IF NOT EXISTS idx_chapters_version_id ON chapters(version_id);
CREATE INDEX IF NOT EXISTS idx_chapters_search ON chapters USING GIN(search_vector);

-- Step 6: Update alembic version table
UPDATE alembic_version SET version_num = '002' WHERE version_num = '001';

-- Done! The old tables are preserved as documents_old and sections_old
-- You can drop them later after verifying the migration worked:
-- DROP TABLE IF EXISTS sections_old CASCADE;
-- DROP TABLE IF EXISTS documents_old CASCADE;
