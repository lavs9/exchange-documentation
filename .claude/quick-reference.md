# Quick Reference Guide

## Project Essentials

### Start Development Environment
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
Common Commands
bash# Backend
docker-compose exec backend pytest                    # Run tests
docker-compose exec backend alembic upgrade head      # Run migrations
docker-compose exec backend black app/                # Format code
docker-compose exec backend ruff app/                 # Lint code

# Frontend
docker-compose exec frontend npm test                 # Run tests
docker-compose exec frontend npm run build            # Build for production

# Database
docker-compose exec postgres psql -U docuser -d exchange_docs
Key Design Decisions
Why Docling?

Best accuracy for structured documents with tables
Active development and support
Handles NSE document complexity well

Why PostgreSQL over MongoDB?

Excellent full-text search (tsvector)
ACID compliance for data integrity
Structured data fits relational model
Proven performance at scale

Why React over Vue/Svelte?

Larger ecosystem and community
Better TypeScript support
Team familiarity
More libraries for markdown/syntax highlighting

Common Patterns
Backend: Creating a New Service
python# app/services/my_service.py
from sqlalchemy.ext.asyncio import AsyncSession

class MyService:
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def do_something(self, param: str) -> Result:
        # Implementation
        pass
Backend: Creating an API Endpoint
python# app/api/my_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter(prefix="/api/my-resource", tags=["my-resource"])

@router.get("/{id}")
async def get_resource(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    # Implementation
    pass
Frontend: Creating a Component
typescript// src/components/MyComponent.tsx
import React, { useState, useEffect } from 'react';

interface MyComponentProps {
  prop1: string;
  onAction?: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ 
  prop1, 
  onAction 
}) => {
  const [state, setState] = useState<string>('');
  
  useEffect(() => {
    // Effect logic
  }, [prop1]);
  
  return (
    <div className="my-component">
      {/* JSX */}
    </div>
  );
};
Frontend: API Call Pattern
typescript// src/services/api.ts
import { apiClient } from './apiClient';

export const myApi = {
  async getResource(id: string): Promise<Resource> {
    try {
      const response = await apiClient.get<Resource>(`/resources/${id}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch resource:', error);
      throw new ApiError('Failed to fetch resource', error);
    }
  }
};
Debugging Tips
Backend Issues

Check logs: docker-compose logs -f backend
Database state: Connect to PostgreSQL and inspect tables
API testing: Use /docs endpoint for interactive testing
Breakpoints: Add import pdb; pdb.set_trace() for debugging

Frontend Issues

Check console: Open browser DevTools
React DevTools: Install extension for component inspection
Network tab: Inspect API calls and responses
Redux DevTools: Not needed in Phase 1 (simple state)

Common Errors
"ModuleNotFoundError" (Backend)
bash# Rebuild backend container
docker-compose build backend
docker-compose up -d backend
"Cannot connect to database"
bash# Check PostgreSQL is running
docker-compose ps postgres
# Check connection string in .env
# Try restarting: docker-compose restart postgres
"CORS Error" (Frontend → Backend)

Check CORS middleware in backend/app/main.py
Ensure allow_origins includes http://localhost:3000

"File not found" (PDF Upload)

Check UPLOAD_DIR environment variable
Ensure directory exists and has write permissions
Check Docker volume mounting in docker-compose.yml

Performance Profiling
Backend
python# Add timing decorator
import time
from functools import wraps

def timing(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await f(*args, **kwargs)
        print(f"{f.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

@timing
async def slow_function():
    pass
Frontend
typescript// Use React DevTools Profiler
// Or add console.time
console.time('render');
// ... render logic
console.timeEnd('render');
Security Checklist (Phase 1)

 File upload validation (MIME type, size)
 SQL injection protection (using ORM)
 Path traversal prevention (sanitize filenames)
 XSS protection (react-markdown handles)
 CORS configuration (localhost only)
 Environment variables for secrets (DATABASE_URL)

Release Checklist
Before Deployment

 All tests pass (pytest, npm test)
 No linting errors (ruff, eslint)
 Database migrations applied
 Environment variables configured
 Documentation updated
 Sample documents tested

Deployment (Phase 1 - Local)
bash# Pull latest code
git pull origin main

# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify
curl http://localhost:8000/health
Useful Resources
Documentation

FastAPI: https://fastapi.tiangolo.com/
React: https://react.dev/
PostgreSQL FTS: https://www.postgresql.org/docs/current/textsearch.html
Docling: https://github.com/DS4SD/docling

Tools

Postman: For API testing
pgAdmin: For PostgreSQL GUI (add to docker-compose if needed)
React DevTools: Browser extension
SQLAlchemy docs: https://docs.sqlalchemy.org/

Data Models Quick Reference
Document
python{
  "id": "uuid",
  "title": "NSE NNF Protocol",
  "version": "6.2",
  "upload_date": "2025-01-15T10:30:00Z",
  "file_path": "/uploads/doc.pdf",
  "page_count": 242,
  "processing_status": "completed",  # processing | completed | failed
  "metadata": {}
}
Section
python{
  "id": "uuid",
  "document_id": "uuid",
  "level": 1,  # 1=Chapter, 2=Section, 3=Subsection, 4=Sub-subsection
  "title": "Chapter 1: Introduction",
  "content": "markdown content...",
  "page_number": 12,
  "parent_id": null,  # or parent section uuid
  "order_index": 1
}
Table of Contents Entry
typescript{
  sectionId: "uuid",
  title: "Chapter 1: Introduction",
  level: 1,
  pageNumber: 12,
  children: [
    {
      sectionId: "uuid",
      title: "Section 1.1",
      level: 2,
      pageNumber: 13,
      children: []
    }
  ]
}
Search Result
typescript{
  sectionId: "uuid",
  sectionTitle: "Chapter 4 - Order Entry",
  pageNumber: 46,
  snippet: "...The transaction code is <mark>BOARD_LOT_IN</mark> (2000)...",
  matchScore: 0.85
}
Environment Variables
Backend (.env)
envDATABASE_URL=postgresql://docuser:docpass@postgres:5432/exchange_docs
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=50
LOG_LEVEL=INFO
Frontend (.env)
envVITE_API_URL=http://localhost:8000
Database Quick Queries
Check document processing status
sqlSELECT id, title, processing_status, upload_date 
FROM documents 
ORDER BY upload_date DESC;
Count sections per document
sqlSELECT d.title, COUNT(s.id) as section_count
FROM documents d
LEFT JOIN sections s ON d.id = s.document_id
GROUP BY d.id, d.title;
Search across all documents
sqlSELECT d.title, s.title, s.page_number
FROM sections s
JOIN documents d ON s.document_id = d.id
WHERE s.search_vector @@ plainto_tsquery('english', 'BOARD_LOT_IN')
ORDER BY ts_rank(s.search_vector, plainto_tsquery('english', 'BOARD_LOT_IN')) DESC;
View TOC structure for a document
sqlSELECT 
    REPEAT('  ', level - 1) || title as indented_title,
    level,
    page_number
FROM sections
WHERE document_id = 'your-doc-uuid'
ORDER BY order_index;
API Quick Reference
Upload Document
bashcurl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/document.pdf" \
  -F "title=NSE NNF Protocol" \
  -F "version=6.2"
List Documents
bashcurl http://localhost:8000/api/documents
Get Document
bashcurl http://localhost:8000/api/documents/{doc_id}
Get Table of Contents
bashcurl http://localhost:8000/api/documents/{doc_id}/toc
Search Document
bashcurl "http://localhost:8000/api/documents/{doc_id}/search?q=BOARD_LOT_IN&page=1&limit=20"
Delete Document
bashcurl -X DELETE http://localhost:8000/api/documents/{doc_id}
Keyboard Shortcuts (Frontend)

Ctrl/Cmd + K - Focus search bar
Ctrl/Cmd + F - Browser find (searches current view)
Esc - Close modals/dialogs
Arrow Up/Down - Navigate search results
Enter - Jump to selected search result

Troubleshooting Flowchart
Issue occurs
    ↓
Is it backend or frontend?
    ↓
Backend:
    ↓
Check logs → docker-compose logs -f backend
    ↓
Database issue? → Check PostgreSQL connection
    ↓
API error? → Test endpoint in /docs
    ↓
Still stuck? → Add pdb breakpoint

Frontend:
    ↓
Check browser console for errors
    ↓
Network tab → Check API responses
    ↓
React DevTools → Inspect component state
    ↓
Still stuck? → Add console.log debugging
Performance Benchmarks (Target)

Document upload: < 30 seconds for 50MB file
PDF processing: < 2 minutes for 300 pages
Search query: < 500ms
TOC generation: < 5 seconds
Page load: < 2 seconds
Section navigation: < 100ms

Contact & Support
For Questions

Check existing documentation first
Search GitHub issues
Ask in team chat

Reporting Bugs
Use .claude/prompts/bug-fix.md template
Feature Requests
Use .claude/prompts/feature-implementation.md template