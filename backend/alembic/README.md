# Database Migrations

This directory contains Alembic database migrations for the Exchange Documentation Manager.

## Overview

We use **Alembic** for database schema version control and migrations. The migration system is configured for async SQLAlchemy with PostgreSQL.

## Files

- `alembic.ini` - Alembic configuration file
- `env.py` - Migration environment setup (async-compatible)
- `script.py.mako` - Template for generating new migrations
- `versions/` - Directory containing all migration scripts

## Initial Setup

The initial schema is created in two ways:

1. **Docker Init** (Recommended for development): The `init.sql` file automatically creates the schema when the PostgreSQL container starts
2. **Alembic Migrations**: Can be used for production deployments or updates

## Common Commands

### View Current Migration Status
```bash
# From backend directory
alembic current
```

### Upgrade to Latest Version
```bash
alembic upgrade head
```

### Downgrade One Version
```bash
alembic downgrade -1
```

### Create New Migration
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration
alembic revision -m "description of changes"
```

### View Migration History
```bash
alembic history
```

## Migration Naming Convention

Migrations follow this pattern:
```
YYYYMMDD_HHMM-XXX_description.py
```

Example:
```
20251007_1050-001_initial_schema.py
```

## Database Schema

### documents
- `id` (UUID, PK)
- `title` (VARCHAR(255))
- `version` (VARCHAR(50))
- `upload_date` (TIMESTAMP)
- `file_path` (VARCHAR(500))
- `page_count` (INTEGER, nullable)
- `processing_status` (VARCHAR(50), default: 'pending')
- `metadata` (JSONB, nullable)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP, auto-updated)

### sections
- `id` (UUID, PK)
- `document_id` (UUID, FK -> documents.id, CASCADE)
- `level` (INTEGER)
- `title` (VARCHAR(500))
- `content` (TEXT)
- `page_number` (INTEGER, nullable)
- `parent_id` (UUID, FK -> sections.id, CASCADE, nullable)
- `order_index` (INTEGER)
- `search_vector` (TSVECTOR, generated)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP, auto-updated)

### Indexes
- `idx_sections_document` - sections(document_id)
- `idx_sections_parent` - sections(parent_id)
- `idx_sections_order` - sections(document_id, order_index)
- `idx_sections_fts` - sections(search_vector) GIN index
- `idx_documents_status` - documents(processing_status)

## Important Notes

1. **Async Support**: The env.py is configured for async SQLAlchemy operations
2. **Generated Columns**: The `search_vector` column is auto-generated for full-text search
3. **Triggers**: `updated_at` columns are automatically updated via PostgreSQL triggers
4. **Cascade Deletes**: Deleting a document cascades to all its sections

## Troubleshooting

### Migration Conflicts
If you encounter migration conflicts:
```bash
# Check current state
alembic current

# If needed, stamp current version
alembic stamp head
```

### Reset Database
To completely reset (development only):
```bash
# Stop containers
docker-compose down -v

# Restart (init.sql will recreate schema)
docker-compose up
```

## Production Deployment

For production deployments:

1. Backup database first
2. Test migrations in staging
3. Run migrations:
   ```bash
   alembic upgrade head
   ```
4. Verify schema matches models

## Adding New Migrations

When modifying models:

1. Update SQLAlchemy models in `app/models/`
2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "add new column"
   ```
3. Review generated migration file
4. Test migration:
   ```bash
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```
5. Commit migration file to git
