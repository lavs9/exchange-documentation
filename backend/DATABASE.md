# Database Architecture

Complete database documentation for the Exchange Documentation Manager.

## Overview

- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Full-Text Search**: PostgreSQL `tsvector` with GIN indexes

## Schema Diagram

```
┌─────────────────────────────────┐
│         documents               │
├─────────────────────────────────┤
│ id              UUID PK         │
│ title           VARCHAR(255)    │
│ version         VARCHAR(50)     │
│ upload_date     TIMESTAMP       │
│ file_path       VARCHAR(500)    │
│ page_count      INTEGER         │
│ processing_status VARCHAR(50)   │
│ metadata        JSONB           │
│ created_at      TIMESTAMP       │
│ updated_at      TIMESTAMP       │
└─────────────────────────────────┘
                  │
                  │ 1:N
                  ▼
┌─────────────────────────────────┐
│          sections               │
├─────────────────────────────────┤
│ id              UUID PK         │
│ document_id     UUID FK         │
│ level           INTEGER         │
│ title           VARCHAR(500)    │
│ content         TEXT            │
│ page_number     INTEGER         │
│ parent_id       UUID FK (self)  │
│ order_index     INTEGER         │
│ search_vector   TSVECTOR (gen)  │
│ created_at      TIMESTAMP       │
│ updated_at      TIMESTAMP       │
└─────────────────────────────────┘
         │
         │ self-referential
         ▼
    (parent-child hierarchy)
```

## Tables

### documents

Stores uploaded PDF documents and their metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Auto-generated unique identifier |
| title | VARCHAR(255) | NOT NULL | Document title (e.g., "NSE NNF Protocol") |
| version | VARCHAR(50) | NOT NULL | Document version (e.g., "v6.2") |
| upload_date | TIMESTAMP | NOT NULL, DEFAULT NOW | When document was uploaded |
| file_path | VARCHAR(500) | NOT NULL | Path to PDF file on disk |
| page_count | INTEGER | NULLABLE | Number of pages in PDF |
| processing_status | VARCHAR(50) | NOT NULL, DEFAULT 'pending' | Status: pending, processing, completed, failed |
| metadata | JSONB | NULLABLE | Additional metadata (e.g., author, tags) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | Record creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW | Last update time (auto-updated) |

**Indexes:**
- `idx_documents_status` on `processing_status`

### sections

Stores document sections with hierarchical structure and full-text search.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Auto-generated unique identifier |
| document_id | UUID | FK -> documents.id, NOT NULL, CASCADE | Parent document |
| level | INTEGER | NOT NULL | Heading level (1=Chapter, 2=Section, etc.) |
| title | VARCHAR(500) | NOT NULL | Section title |
| content | TEXT | NOT NULL | Section content in Markdown |
| page_number | INTEGER | NULLABLE | Page number in original PDF |
| parent_id | UUID | FK -> sections.id, NULLABLE, CASCADE | Parent section (for hierarchy) |
| order_index | INTEGER | NOT NULL | Order within document |
| search_vector | TSVECTOR | GENERATED, STORED | Full-text search index |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | Record creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW | Last update time (auto-updated) |

**Indexes:**
- `idx_sections_document` on `document_id`
- `idx_sections_parent` on `parent_id`
- `idx_sections_order` on `(document_id, order_index)`
- `idx_sections_fts` on `search_vector` (GIN index)

**Generated Column:**
```sql
search_vector tsvector GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
) STORED
```

## Relationships

### documents → sections (One-to-Many)
- A document can have many sections
- Deleting a document cascades to all its sections

### sections → sections (Self-Referential)
- A section can have a parent section
- A section can have many child sections
- Deleting a parent cascades to all children

## Full-Text Search

PostgreSQL's built-in full-text search is used for searching document content.

### Search Query Example
```sql
SELECT
    s.id,
    s.title,
    s.page_number,
    ts_headline('english', s.content, query,
        'MaxWords=50, MinWords=25') as snippet,
    ts_rank(search_vector, query) as rank
FROM sections s, plainto_tsquery('english', 'trade settlement') query
WHERE s.document_id = $1
  AND s.search_vector @@ query
ORDER BY rank DESC, s.order_index
LIMIT 20 OFFSET 0;
```

### Search Features
- **Language**: English (configurable)
- **Ranking**: `ts_rank` for relevance scoring
- **Snippets**: `ts_headline` for context snippets
- **Performance**: GIN index on `search_vector` column

## Triggers

### update_updated_at_column()
Automatically updates the `updated_at` timestamp when a record is modified.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

**Applied to:**
- `documents` table
- `sections` table

## SQLAlchemy Models

### Document Model
```python
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    # ... other fields

    # Relationship
    sections: Mapped[list["Section"]] = relationship(
        "Section",
        back_populates="document",
        cascade="all, delete-orphan",
    )
```

### Section Model
```python
class Section(Base):
    __tablename__ = "sections"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    # ... other fields

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="sections")
    parent: Mapped["Section | None"] = relationship(
        "Section",
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[list["Section"]] = relationship(
        "Section",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
```

## Pydantic Schemas

### Request/Response Models
- `DocumentCreate` - For creating documents
- `DocumentResponse` - For document responses
- `DocumentWithSections` - Document with nested sections
- `SectionCreate` - For creating sections
- `SectionResponse` - For section responses
- `TableOfContents` - Hierarchical TOC structure
- `SearchResults` - Search results with snippets

See [app/schemas/document.py](app/schemas/document.py) for complete schemas.

## Data Access Patterns

### Query Documents with Sections
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Eager load sections
result = await session.execute(
    select(Document)
    .options(selectinload(Document.sections))
    .where(Document.id == document_id)
)
document = result.scalar_one()
```

### Build TOC Hierarchy
```python
# Get sections ordered by order_index
result = await session.execute(
    select(Section)
    .where(Section.document_id == document_id)
    .order_by(Section.order_index)
)
sections = result.scalars().all()

# Build tree structure based on parent_id
# (Implementation in TOCGenerator service)
```

### Full-Text Search
```python
from sqlalchemy import text

# Raw SQL for full-text search
query = text("""
    SELECT s.*, ts_rank(search_vector, query) as rank
    FROM sections s, plainto_tsquery('english', :search_term) query
    WHERE s.document_id = :doc_id
      AND s.search_vector @@ query
    ORDER BY rank DESC
    LIMIT :limit OFFSET :offset
""")

result = await session.execute(
    query,
    {
        "search_term": "settlement process",
        "doc_id": document_id,
        "limit": 20,
        "offset": 0
    }
)
```

## Performance Considerations

### Indexes
1. **Document Status**: For filtering by processing status
2. **Section Document**: For joining sections to documents
3. **Section Parent**: For traversing hierarchy
4. **Section Order**: For retrieving sections in sequence
5. **Full-Text Search**: GIN index for fast text search

### Query Optimization
- Use `selectinload()` for eager loading relationships
- Paginate large result sets (default: 20 items)
- Use database connection pooling (SQLAlchemy default: 5-10)
- Leverage prepared statements via ORM

### Scaling Considerations
- **Read Replicas**: For high read workloads
- **Partitioning**: sections table by document_id (future)
- **Caching**: Redis for frequently accessed documents (future)
- **Archive**: Move old documents to cold storage (future)

## Migration Management

See [alembic/README.md](alembic/README.md) for:
- Creating new migrations
- Applying migrations
- Rollback procedures
- Version control

## Data Integrity

### Constraints
- Foreign key constraints with CASCADE deletes
- NOT NULL constraints on required fields
- Check constraints on level (1-6 via Pydantic validation)

### Validation
- Pydantic schemas validate input at API layer
- SQLAlchemy validates at ORM layer
- PostgreSQL enforces constraints at database layer

### Transactions
All write operations use transactions:
```python
async with session.begin():
    session.add(document)
    # Add sections
    await session.commit()
```

## Backup & Recovery

### Docker Development
- Volume: `postgres_data` persists data
- Backup: `docker exec exchange-doc-db pg_dump -U postgres exchange_docs > backup.sql`
- Restore: `docker exec -i exchange-doc-db psql -U postgres exchange_docs < backup.sql`

### Production
- Regular pg_dump snapshots
- Point-in-time recovery (PITR) with WAL archiving
- Replication for high availability

## Testing

### Test Database
```python
# Use separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/exchange_docs_test"

# Reset between tests
async def reset_database():
    await engine.dispose()
    # Drop and recreate tables
```

### Fixtures
```python
@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
```

## Future Enhancements

- [ ] Add `document_versions` table for version tracking
- [ ] Add `annotations` table for user comments
- [ ] Implement soft deletes with `deleted_at` column
- [ ] Add audit logging table
- [ ] Partition sections table by document_id
- [ ] Add materialized views for analytics
