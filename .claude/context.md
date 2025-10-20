# Exchange API Documentation Manager - Context

## Project Overview
A specialized documentation management system that transforms NSE (National Stock Exchange of India) API PDFs into searchable, navigable web documents with table of contents and full-text search capabilities.

## Current Phase
**Phase 1 (POC)**: Core Document Processing & Navigation
- Duration: 7 weeks
- Status: Starting development
- Goal: Prove PDF → structured format conversion feasibility

## Key Constraints
- **Scope**: NSE documents only (initially 4-5 documents)
- **Authentication**: None required in Phase 1
- **Deployment**: Local only (Docker Compose)
- **Users**: Single-user system

## Technology Stack
### Backend
- Python 3.11+ with FastAPI
- PostgreSQL 15 (with full-text search)
- Docling for PDF parsing
- Poetry for dependency management

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- react-markdown for rendering
- Vite as build tool

### Infrastructure
- Docker & Docker Compose
- Local file system storage

## Core Features (Phase 1)
1. **PDF Ingestion**: Upload NSE PDFs and parse into structured format
2. **Table of Contents**: Auto-generated, 4-level nested, collapsible TOC
3. **Full-Text Search**: PostgreSQL-powered search with highlighting
4. **Document Viewer**: Markdown rendering with syntax highlighting
5. **Document Management**: List, view, delete documents

## Success Criteria
- Process 300-page PDF in < 2 minutes
- Search results in < 500ms
- 95%+ accuracy in structure extraction
- One-command Docker setup

## Reference Document
Primary test document: NSE NNF Protocol v6.2 (242 pages)
- Contains: chapters, sections, tables, code blocks, transaction codes
- Structure: Hierarchical with up to 4 nesting levels

## Out of Scope (Phase 1)
- User authentication
- Annotations/comments
- Version comparison
- Multi-user support
- Cloud deployment
- BSE/MCX documents
- Mobile optimization

## Development Phases
- **Phase 1** (Current): Core processing & navigation
- **Phase 2** (Future): Annotations & collaboration
- **Phase 3** (Future): Version management & diff
- **Phase 4** (Future): AI integration & multi-document

## Key Files & Directoriesexchange-doc-manager/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── services/     # Business logic (PDF parsing, search)
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/   # React components (TOC, Viewer, Search)
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
└── docker-compose.yml

## Important Considerations
1. **PDF Parsing Accuracy**: Docling may need custom post-processors
2. **Table Preservation**: Complex tables require special handling
3. **Search Performance**: Use PostgreSQL GIN indexes
4. **TOC Generation**: Must handle irregular heading hierarchies
5. **Memory Management**: Large PDFs need streaming/chunking

## External Dependencies
- Docling: Primary PDF parsing library
- PostgreSQL FTS: Full-text search engine
- No external APIs or cloud services

## Testing Strategy
- Unit tests for parsing logic
- Integration tests for API endpoints
- Test with actual NSE NNF Protocol v6.2
- Performance benchmarks for search & processing