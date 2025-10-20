# Database Migration Prompt Template

When creating database migrations, provide:

## Migration Purpose
- Summary: [e.g., "Add full-text search index to sections table"]
- Ticket/Issue: [Reference if applicable]
- Migration Type: [Schema change / Data migration / Both]

## Schema Changes
- [ ] Add table
- [ ] Modify table (add/remove/alter columns)
- [ ] Add index
- [ ] Add constraint
- [ ] Data migration required

## Current Schema
```sql
[Paste current relevant schema]
Desired Schema
sql[Paste desired schema or describe changes]
Example
Adding a new column:
sql-- Current
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL
);

-- Desired
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    file_size BIGINT  -- NEW COLUMN
);
Adding an index:
sqlCREATE INDEX idx_sections_fts ON sections USING GIN(search_vector);
Data Migration Required?

 Yes - describe data transformation needed
 No - pure schema change

If Yes, describe transformation:
Example: 
- Populate new file_size column by reading from filesystem
- Convert existing timestamps from UTC to local timezone
- Backfill search_vector column using existing content
Rollback Plan

How to rollback: [Describe rollback procedure]
Data loss risk: [None/Low/Medium/High]
Reversible: [Yes/No]

Rollback Commands
sql[Paste rollback SQL if applicable]
Performance Considerations

Estimated migration time: [e.g., "< 1 minute for 5 documents"]
Downtime required: [Yes/No]
Index building: [Online/Offline]
Table locking: [Will table be locked during migration?]
Large table impact: [Will this affect large tables?]

Testing Strategy

 Test on sample data
 Verify queries still work
 Check performance impact
 Test rollback procedure
 Verify data integrity

Test Commands
sql[Paste SQL queries to verify migration success]
Dependencies

Required before: [List any prerequisite migrations]
Blocks: [List any migrations that must wait for this one]
Related migrations: [Any related schema changes]

Alembic Migration Details
Migration File Name
[timestamp]_[description].py
Example: 2025_01_15_1430_add_fulltext_search_index.py
Expected Alembic Commands
bash# Create migration
alembic revision --autogenerate -m "add full-text search index"

# Review generated migration file
cat alembic/versions/[timestamp]_add_fulltext_search_index.py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
Code Changes Required
Models (SQLAlchemy)
python# app/models/section.py
[Show any model changes needed]
Schemas (Pydantic)
python# app/schemas/section.py
[Show any schema changes needed]
Services
python# app/services/[service_name].py
[Show any service logic changes needed]
Verification Queries
After Migration - Run These
sql-- Verify new column exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'your_table';

-- Verify index created
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'your_table';

-- Check data integrity
SELECT COUNT(*) FROM your_table WHERE new_column IS NULL;

-- Test query performance
EXPLAIN ANALYZE 
SELECT * FROM sections 
WHERE search_vector @@ plainto_tsquery('test');
Impact Analysis
Affected Components

 API endpoints: [List affected endpoints]
 Background jobs: [List affected jobs]
 External integrations: [Any external systems affected]

Breaking Changes

 Yes - describe impact
 No

Backward Compatibility

 Fully backward compatible
 Requires code deployment
 Requires configuration changes

Example Migration Template
python"""add full-text search index

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2025-01-15 14:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None


def upgrade():
    # Add generated column for search vector
    op.execute("""
        ALTER TABLE sections 
        ADD COLUMN search_vector tsvector 
        GENERATED ALWAYS AS (
            to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
        ) STORED;
    """)
    
    # Create GIN index
    op.create_index(
        'idx_sections_fts',
        'sections',
        ['search_vector'],
        postgresql_using='gin'
    )


def downgrade():
    # Drop index first
    op.drop_index('idx_sections_fts', table_name='sections')
    
    # Drop column
    op.drop_column('sections', 'search_vector')
Risk Assessment
High Risk Factors

 Large table (>1M rows)
 Production downtime required
 Data transformation complex
 Rollback difficult/impossible

Mitigation Strategies
Example:
- Run during low-traffic window
- Create index CONCURRENTLY to avoid locks
- Test on production-sized dataset first
- Have rollback plan ready
Checklist Before Applying

 Migration reviewed by team
 Tested on development database
 Tested with production-sized data
 Rollback plan documented and tested
 Performance impact assessed
 Backup created (for production)
 Monitoring in place to detect issues

Post-Migration Actions

 Verify migration success with queries above
 Monitor application logs for errors
 Check API endpoint performance
 Update documentation if needed
 Notify team of completion


Use Alembic for all migrations. Follow conventions in .claude/conventions.md and reference database schema in .claude/architecture.md.