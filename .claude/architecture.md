markdown# System Architecture

## High-Level Architecture (UPDATED)
```
┌─────────────────────────────────────────────────────────┐
│                     User Browser                        │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Frontend (React)                       │
│  ┌──────────────┬──────────────┬───────────────────┐   │
│  │ Document     │ TOC          │ Search            │   │
│  │ Viewer       │ Navigator    │ Interface         │   │
│  └──────────────┴──────────────┴───────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API
                      ▼
┌─────────────────────────────────────────────────────────┐
│                Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ API Layer (FastAPI Routes)                       │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Service Layer                                    │  │
│  │  ├─ DocumentProcessor (JSON/MD → Structured)    │  │
│  │  ├─ RichMarkdownGenerator (JSON → Rich MD)      │  │
│  │  ├─ SearchService (PostgreSQL FTS)              │  │
│  │  └─ TOCGenerator (Hierarchy builder)            │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Data Layer (SQLAlchemy ORM)                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        ▼                            ▼
┌──────────────────┐      ┌──────────────────┐
│   PostgreSQL     │      │  File System     │
│   - documents    │      │  - uploads/      │
│   - sections     │      │    (JSON/MD)     │
│   - FTS indexes  │      └──────────────────┘
└──────────────────┘
```
└──────────────────┘

## Component Responsibilities

### Frontend Components

#### 1. DocumentList
- Displays uploaded documents with metadata
- Handles upload initiation
- Manages document selection/deletion
- Shows processing status

#### 2. TableOfContents
- Recursive component for nested TOC
- Handles expand/collapse state
- Scroll-to-section functionality
- Active section highlighting (Intersection Observer)

#### 3. DocumentViewer
- Renders markdown content
- Syntax highlighting for code blocks
- Responsive table handling
- Copy-to-clipboard for code

#### 4. SearchBar
- Real-time search input
- Result list with snippets
- Jump-to-result navigation
- Search term highlighting

### Backend Services

#### 1. DocumentProcessor
**Purpose**: Orchestrates PDF → Structured document conversion

**Flow**:
```python
1. Receive PDF file
2. Save to file system
3. Create database record (status='processing')
4. Call PDFParser.parse()
5. Call TOCGenerator.generate()
6. Store sections in database
7. Update status to 'completed'
Key Methods:

process_document(file: UploadFile) -> Document
get_processing_status(doc_id: str) -> ProcessingStatus

2. PDFParser
Purpose: Extract content from PDF using Docling
Flow:
python1. Initialize Docling DocumentConverter
2. Convert PDF → Markdown
3. Extract sections using heading patterns
4. Parse tables into structured format
5. Identify code blocks
6. Return List[Section] with hierarchy
Key Methods:

parse_pdf(file_path: str) -> List[Section]
extract_tables(markdown: str) -> List[Table]
detect_code_blocks(markdown: str) -> List[CodeBlock]

Custom Post-Processing:

Fix heading hierarchy (Chapter → Section → Subsection)
Preserve table column alignment
Maintain code indentation
Extract transaction code tables

3. SearchService
Purpose: Full-text search using PostgreSQL
Query Strategy:
sql-- Use tsvector for indexed search
SELECT 
    s.id,
    s.title,
    s.page_number,
    ts_headline('english', s.content, query, 
        'MaxWords=50, MinWords=25') as snippet,
    ts_rank(search_vector, query) as rank
FROM sections s, plainto_tsquery('english', ?) query
WHERE s.document_id = ?
  AND s.search_vector @@ query
ORDER BY rank DESC, s.order_index
LIMIT ? OFFSET ?;
Key Methods:

search(query: str, doc_id: str, filters: SearchFilters) -> SearchResults
highlight_terms(content: str, query: str) -> str

4. TOCGenerator
Purpose: Build hierarchical table of contents
Algorithm:
python1. Iterate through sections in order
2. Track current path (stack of parent sections)
3. Based on level:
   - If level > parent.level: Add as child
   - If level == parent.level: Add as sibling
   - If level < parent.level: Pop stack and add
4. Build recursive TOCEntry tree
Key Methods:

generate_toc(sections: List[Section]) -> TableOfContents
build_tree(flat_sections: List[Section]) -> List[TOCEntry]

Data Flow Diagrams
Document Upload Flow
User → Upload File
  ↓
Frontend → POST /api/documents/upload
  ↓
API Layer → Validate file (size, type)
  ↓
DocumentProcessor → Save to file system
  ↓
DocumentProcessor → Create DB record (processing)
  ↓
PDFParser → Extract sections with Docling
  ↓
TOCGenerator → Build hierarchy
  ↓
Data Layer → Store sections in PostgreSQL
  ↓
DocumentProcessor → Update status (completed)
  ↓
API Layer → Return document_id
  ↓
Frontend → Poll for status / Display document
Search Flow
User → Type query
  ↓
Frontend → GET /api/documents/{id}/search?q=query
  ↓
API Layer → Validate & sanitize query
  ↓
SearchService → Execute PostgreSQL FTS query
  ↓
PostgreSQL → Return ranked results with snippets
  ↓
SearchService → Format results (highlight terms)
  ↓
API Layer → Return SearchResults JSON
  ↓
Frontend → Display results with snippets
  ↓
User → Click result
  ↓
Frontend → Scroll to section
Database Schema
documents Table
sqlCREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    upload_date TIMESTAMP NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    page_count INTEGER,
    processing_status VARCHAR(50) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
sections Table
sqlCREATE TABLE sections (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    level INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    parent_id UUID REFERENCES sections(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
    ) STORED,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_sections_document ON sections(document_id);
CREATE INDEX idx_sections_parent ON sections(parent_id);
CREATE INDEX idx_sections_order ON sections(document_id, order_index);
CREATE INDEX idx_sections_fts ON sections USING GIN(search_vector);
API Endpoints
Document Management

POST /api/documents/upload - Upload PDF
GET /api/documents - List all documents
GET /api/documents/{id} - Get document metadata
DELETE /api/documents/{id} - Delete document
GET /api/documents/{id}/status - Check processing status

Navigation

GET /api/documents/{id}/toc - Get table of contents
GET /api/documents/{id}/sections/{section_id} - Get section content

Search

GET /api/documents/{id}/search - Search within document

Performance Optimizations
Backend

Database Indexing: GIN indexes for full-text search
Connection Pooling: SQLAlchemy async engine
Lazy Loading: Load sections on-demand
Chunked Processing: Stream large PDFs

Frontend

Code Splitting: Lazy load components
Virtual Scrolling: For long documents (if needed in future)
Debounced Search: 300ms delay on search input
Memoization: React.memo for TOC entries

Error Handling Strategy
Backend

Custom exception classes (DocumentProcessingError, SearchError)
Global exception handler in FastAPI
Structured error responses with codes
Logging with context (document_id, user_action)

Frontend

Error boundaries for component crashes
Toast notifications for user errors
Retry logic for failed API calls
Graceful degradation (e.g., show raw markdown if renderer fails)

Security Considerations (Phase 1)

File Upload: Validate MIME type, size limits
Path Traversal: Sanitize file names
SQL Injection: Use parameterized queries (SQLAlchemy ORM)
XSS: Sanitize markdown output (react-markdown handles this)
CORS: Restrict to localhost in Docker setup

Scalability Path (Future Phases)
Phase 2 (Annotations)

Add annotations table linked to sections
Implement WebSocket for real-time collaboration

Phase 3 (Versioning)

Add document_versions table
Implement diff algorithm (Python difflib or custom)
Migration strategy for annotations

Phase 4 (Cloud & Multi-user)

Replace PostgreSQL with RDS/Cloud SQL
Add S3/GCS for file storage
Implement authentication (OAuth2)
Add Redis for caching
Horizontal scaling with load balancer


## Document Processing Flow (UPDATED)

**IMPORTANT**: The application does NOT parse PDFs directly. Users must provide pre-processed Docling JSON or Markdown files.
```
External Tool → Docling JSON/Markdown
                      ↓
              Upload to System
                      ↓
         ┌────────────┴────────────┐
         │                         │
    JSON Input               Markdown Input
         ↓                         ↓
RichMarkdownGenerator        Direct Processing
         ↓                         ↓
    Rich Markdown            Rich Markdown
         ↓                         ↓
         └────────────┬────────────┘
                      ↓
              Store in Database
                      ↓
         Frontend Markdown Renderer
```

### Why This Approach?

1. **Memory Constraints**: PDF parsing with Docling requires significant memory, causing Docker crashes
2. **Separation of Concerns**: PDF processing happens externally, application focuses on document management
3. **Flexibility**: Users can pre-process PDFs using any environment (local machine, cloud, etc.)
4. **Future Enhancement**: PDF parsing can be added later as an optional async job

## Component Responsibilities (UPDATED)

### Backend Services

#### 1. DocumentProcessor (UPDATED)
**Purpose**: Orchestrates JSON/Markdown → Structured document conversion

**Flow**:
```python
1. Receive Docling JSON or Markdown file
2. Save to file system
3. Create database record (status='processing')
4. Detect file type (JSON or Markdown)
5. If JSON: Call RichMarkdownGenerator.generate()
6. If Markdown: Use directly (optionally enhance)
7. Call TOCGenerator.generate()
8. Store sections in database
9. Update status to 'completed'
```

**Key Methods**:
- `process_document(file: UploadFile, file_type: str) -> Document`
- `get_processing_status(doc_id: str) -> ProcessingStatus`

#### 2. RichMarkdownGenerator (NEW)
**Purpose**: Transform Docling JSON into rich, readable markdown

**Docling Document Structure Reference**:
Uses the Docling Core Document model: https://docling-project.github.io/docling/reference/docling_document/#docling_core.types.doc.DoclingDocument

Key classes from Docling:
- `DoclingDocument`: Main document structure
- `DocItem`: Individual document elements (text, table, picture, etc.)
- `TableData`: Structured table representation
- `RefItem`: Cross-references within document

**Flow**:
```python
1. Parse Docling JSON into DoclingDocument object
2. Iterate through document items (DocItem)
3. For each item type:
   - TextItem → Markdown paragraph with inline formatting
   - TableItem → GitHub-flavored markdown table with caption
   - HeadingItem → Markdown heading with page reference
   - CodeItem → Fenced code block with language hint
   - ListItem → Markdown list (ordered/unordered)
   - RefItem → Internal markdown link with anchor
4. Add YAML frontmatter with metadata
5. Insert Obsidian-style callouts for important sections
6. Return rich markdown string
```

**Key Methods**:
- `generate(docling_json: Dict) -> str`
- `_parse_docling_document(json_data: Dict) -> DoclingDocument`
- `_format_table(table_item: TableItem) -> str`
- `_format_heading(heading_item: HeadingItem) -> str`
- `_format_reference(ref_item: RefItem) -> str`
- `_add_callout(text: str, type: str) -> str`

**Rich Markdown Features**:
- ✅ YAML frontmatter for metadata
- ✅ GitHub Flavored Markdown (tables, task lists, strikethrough)
- ✅ Obsidian-style callouts: `> [!note]`, `> [!tip]`, `> [!warning]`
- ✅ Page references: `` `[p.56]` ``
- ✅ Internal links with anchors: `[Chapter 4](#chapter-4-order-entry)`
- ✅ Code blocks with language hints: `` ```python ``
- ✅ Table captions and metadata
- ✅ Inline formatting preservation (bold, italic, code)

#### 3. ~~PDFParser~~ (REMOVED)
**Status**: Not implemented in Phase 1 due to memory constraints.
**Future**: May be added as optional async background job with increased resources.

#### 4. TOCGenerator (UPDATED)
**Purpose**: Build hierarchical table of contents from markdown headings

**Algorithm**:
```python
1. Parse markdown to extract all headings
2. Extract heading level, text, and anchor ID
3. Build tree structure based on levels
4. Track page numbers from inline references
5. Return nested TOCEntry structure
```

**Key Methods**:
- `generate_from_markdown(markdown: str) -> TableOfContents`
- `extract_headings(markdown: str) -> List[Heading]`
- `build_tree(headings: List[Heading]) -> List[TOCEntry]`

#### 5. SearchService (UNCHANGED)
**Purpose**: Full-text search using PostgreSQL

See existing SearchService documentation (no changes).

### Frontend Components (UPDATED)

#### MarkdownRenderer (NEW - REPLACES DocumentViewer)
**Purpose**: Render rich markdown with GitHub/Obsidian styling

**Libraries**:
- `react-markdown`: Core markdown renderer
- `remark-gfm`: GitHub Flavored Markdown support
- `remark-frontmatter`: YAML frontmatter parsing
- `remark-footnotes`: Footnotes support
- `react-syntax-highlighter`: Code block highlighting

**Features**:
- Callout detection and styling
- Syntax-highlighted code blocks
- Responsive tables
- Internal link navigation
- Page reference badges
- Clean, readable typography

**Key Props**:
- `content: string` - Rich markdown content
- `onInternalLinkClick?: (anchor: string) => void` - Handle internal navigation

## Data Flow Diagrams (UPDATED)

### Document Upload Flow (UPDATED)
```
User → Upload Docling JSON or Markdown File
  ↓
Frontend → POST /api/documents/upload (with file_type param)
  ↓
API Layer → Validate file (size, type: json or markdown)
  ↓
DocumentProcessor → Save to file system
  ↓
DocumentProcessor → Create DB record (processing)
  ↓
DocumentProcessor → Detect file type
  ↓
  ├─ If JSON:
  │   ↓
  │   RichMarkdownGenerator → Parse Docling JSON
  │   ↓
  │   RichMarkdownGenerator → Generate rich markdown
  │
  └─ If Markdown:
      ↓
      Use directly (or optionally enhance)
  ↓
TOCGenerator → Extract headings from markdown
  ↓
TOCGenerator → Build hierarchy
  ↓
Data Layer → Store sections in PostgreSQL
  ↓
DocumentProcessor → Update status (completed)
  ↓
API Layer → Return document_id
  ↓
Frontend → Poll for status / Display document
```

### Search Flow (UNCHANGED)
See existing Search Flow documentation (no changes).

## Database Schema (UNCHANGED)

See existing database schema (no changes to tables).

## API Endpoints (UPDATED)

### Document Management
- `POST /api/documents/upload?file_type=json|markdown` - Upload Docling JSON or Markdown
- `GET /api/documents` - List all documents
- `GET /api/documents/{id}` - Get document metadata
- `DELETE /api/documents/{id}` - Delete document
- `GET /api/documents/{id}/status` - Check processing status

### Navigation (UNCHANGED)
- `GET /api/documents/{id}/toc` - Get table of contents
- `GET /api/documents/{id}/sections/{section_id}` - Get section content

### Search (UNCHANGED)
- `GET /api/documents/{id}/search` - Search within document

## Performance Optimizations (UPDATED)

### Backend
1. **No PDF Processing**: Eliminates memory-intensive operation
2. **Fast JSON Parsing**: Using native Python JSON parser
3. **Efficient Markdown Generation**: Single-pass document traversal
4. **Database Indexing**: GIN indexes for full-text search
5. **Connection Pooling**: SQLAlchemy async engine

### Frontend (UNCHANGED)
See existing frontend optimizations (no changes).

## Error Handling Strategy (UPDATED)

### Backend
- Custom exception classes:
  - `DocumentProcessingError`: General processing failures
  - `UnsupportedFileTypeError`: Invalid file type
  - `DoclingJSONParseError`: Malformed Docling JSON
  - `MarkdownGenerationError`: Markdown generation failures
  - `SearchError`: Search failures
- Global exception handler in FastAPI
- Structured error responses with codes
- Logging with context (document_id, file_type, user_action)

### Frontend (UNCHANGED)
See existing error handling (no changes).

## Security Considerations (UPDATED - Phase 1)

- **File Upload**: Validate MIME type (application/json, text/markdown), size limits
- **JSON Validation**: Verify Docling JSON schema before processing
- **Markdown Sanitization**: Prevent XSS through react-markdown configuration
- **Path Traversal**: Sanitize file names
- **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
- **CORS**: Restrict to localhost in Docker setup

## Technology Stack (UPDATED)

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Document Processing**: 
  - Docling Core Types (for parsing JSON structure)
  - Custom RichMarkdownGenerator
- **Database**: PostgreSQL 15 with full-text search
- **Storage**: Local file system (for JSON/Markdown files)
- **Dependencies**: Poetry

### Frontend (UNCHANGED)
See existing frontend stack (no changes).

## External Dependencies (UPDATED)

### Required Python Packages
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
psycopg2-binary = "^2.9.9"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
python-multipart = "^0.0.6"
docling-core = "^1.0.0"  # For Docling document types only
```

**Note**: Full `docling` package (with PDF parsing) is NOT installed to avoid memory issues.

### Required Node Packages
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "remark-frontmatter": "^5.0.0",
    "remark-footnotes": "^4.0.0",
    "react-syntax-highlighter": "^15.5.0"
  }
}
```

# System Architecture (UPDATED - File-Based with Minimal Database)

## High-Level Architecture
```┌─────────────────────────────────────────────────────────┐
│                     User Browser                        │
└─────────────────────┬───────────────────────────────────┘
│ HTTP/REST
▼
┌─────────────────────────────────────────────────────────┐
│                  Frontend (React)                       │
│  ┌──────────────┬──────────────┬───────────────────┐   │
│  │ Document     │ TOC          │ Search            │   │
│  │ Viewer       │ Navigator    │ Interface         │   │
│  └──────────────┴──────────────┴───────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
│ REST API
▼
┌─────────────────────────────────────────────────────────┐
│                Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ API Layer (FastAPI Routes)                       │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Service Layer                                    │  │
│  │  ├─ DocumentProcessor (JSON → Markdown Files)   │  │
│  │  ├─ RichMarkdownGenerator (JSON → Rich MD)      │  │
│  │  ├─ FileStorageService (Read/Write Files)       │  │
│  │  ├─ SearchService (Hybrid: DB Index + Files)    │  │
│  │  └─ TOCGenerator (Parse MD → TOC Tree)          │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Data Layer                                       │  │
│  │  ├─ Metadata DB (PostgreSQL - lightweight)      │  │
│  │  └─ File System (Markdown content storage)      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
│
┌─────────────┴──────────────┐
▼                            ▼
┌──────────────────┐      ┌──────────────────┐
│   PostgreSQL     │      │  File System     │
│   (Metadata)     │      │  storage/        │
│   - documents    │      │   documents/     │
│   - chapters     │      │    nse-nnf/      │
│   - search index │      │     versions/    │
└──────────────────┘      │      v6.3/       │
│       chapters/  │
│       links/     │
└──────────────────┘

## Storage Architecture: Hybrid Approach

### Principle: **Database for Metadata, Files for Content**Content Storage:  Markdown files on disk
Metadata Storage: PostgreSQL (minimal schema)
Search Index:     PostgreSQL (generated from files)

### File System Structurebackend/
storage/
documents/
{document-slug}/              # e.g., "nse-nnf-protocol"
active_version.txt          # Contains: "v6.3"    versions/
      v6.2/
        metadata.json           # Version metadata
        chapters/
          chapter-01-introduction.md
          chapter-02-guidelines.md
          chapter-04-order-entry.md
          chapter-07-broadcast.md
          ...
        links/                  # Linked explanation docs
          chapter-04-order-types-clarification.md
          chapter-07-trade-cancel-explanation.md      v6.3/
        metadata.json
        chapters/
          chapter-01-introduction.md
          ...
        links/
          ...      v6.3-draft/              # Pending approval
        metadata.json
        chapters/
          chapter-01-introduction.md
          ...    diffs/                     # Version comparison
      v6.2-to-v6.3/
        review-status.json
        chapter-01-introduction.diff
        chapter-04-order-entry.diff
        manual-blocks-map.json
        link-blocks-map.json

### File Formats

#### `metadata.json` (Version Metadata)
```json{
"version": "6.3",
"title": "NSE NNF Protocol",
"upload_date": "2025-01-15T10:30:00Z",
"status": "active",
"docling_json_path": "../uploads/nse-v6.3.json",
"total_pages": 242,
"chapters": [
{
"number": 1,
"title": "Introduction",
"file": "chapter-01-introduction.md",
"page_range": "12-25",
"word_count": 1250
},
{
"number": 4,
"title": "Order and Trade Management",
"file": "chapter-04-order-entry.md",
"page_range": "46-72",
"word_count": 5840
}
]
}

#### Chapter Markdown File (with inline markers)
```markdown
title: Order and Trade Management
chapter: 4
pages: 46-72
version: 6.3Chapter 4: Order and Trade Management [p.46]This chapter describes order entry, modification, and cancellation.Section 4.1: Order Entry [p.50]The transaction code is BOARD_LOT_IN (2000).<!-- MANUAL:START:user@example.com:2025-01-15T10:30:00Z -->

[!important] 💡
Production Note: Always validate order quantity before submission.
This prevents common integration errors.

<!-- MANUAL:END -->Regular lot orders are processed in the normal market.<!-- LINK:chapter-04-order-types-clarification.md -->
📎 Exchange Clarification: Order Types
<!-- /LINK -->Order StructureThe order entry request structure is defined below:
Table 19: ORDER_ENTRY_REQUEST
Page 50
FieldTypeSizeOffsetDescriptionTransactionCodeSHORT20The transaction codeUserIdLONG42User ID

#### Linked Document
```markdown
title: Order Types Clarification
created: 2025-01-15
author: product-manager@example.com
linked_to:

chapter-04-order-entry
chapter-04-order-modification

Order Types ClarificationBased on discussion with NSE team on 2025-01-10.Regular Lot vs Special TermsRegular lot orders (RL) are standard market orders...Common ConfusionProduct managers often confuse IOC with Day orders...

#### `review-status.json` (Diff Review State)
```json{
"from_version": "v6.2",
"to_version": "v6.3",
"created_at": "2025-01-15T10:30:00Z",
"status": "pending",
"reviewed_by": null,
"completed_at": null,
"chapters": [
{
"chapter": "chapter-01-introduction",
"status": "no_changes",
"changes_count": 0,
"accepted_changes": 0,
"rejected_changes": 0
},
{
"chapter": "chapter-04-order-entry",
"status": "pending",
"changes_count": 15,
"accepted_changes": 0,
"rejected_changes": 0,
"manual_blocks": [
{
"id": "manual-1",
"type": "callout",
"original_position": "after-heading-order-entry",
"content_preview": "Production Note: Always validate...",
"reanchor_status": "pending"
}
],
"link_blocks": [
{
"id": "link-1",
"target_file": "chapter-04-order-types-clarification.md",
"original_position": "after-paragraph-3",
"reanchor_status": "pending"
}
]
}
]
}

## Database Schema (Minimal Metadata Only)

### Core Principle: **Only metadata, no content**
```sql-- Documents (high-level metadata)
CREATE TABLE documents (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
slug VARCHAR(255) UNIQUE NOT NULL,        -- "nse-nnf-protocol"
title VARCHAR(255) NOT NULL,
active_version VARCHAR(50),               -- "v6.3"
storage_path VARCHAR(500) NOT NULL,       -- "storage/documents/nse-nnf-protocol/"
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()
);-- Document versions
CREATE TABLE document_versions (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
version VARCHAR(50) NOT NULL,
status VARCHAR(20) NOT NULL,              -- "draft", "active", "archived"
metadata_file_path VARCHAR(500),          -- Path to metadata.json
upload_date TIMESTAMP DEFAULT NOW(),
approved_by VARCHAR(255),
approved_at TIMESTAMP,
UNIQUE(document_id, version)
);-- Chapters (metadata + search index)
CREATE TABLE chapters (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
version_id UUID REFERENCES document_versions(id) ON DELETE CASCADE,
chapter_number INT NOT NULL,
title TEXT NOT NULL,
file_path VARCHAR(500) NOT NULL,          -- Relative path to .md file
page_range VARCHAR(50),                   -- "46-72"
word_count INT DEFAULT 0,
has_manual_content BOOLEAN DEFAULT FALSE,
has_linked_docs BOOLEAN DEFAULT FALSE,
search_vector TSVECTOR,                   -- For full-text search
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW(),
UNIQUE(version_id, chapter_number)
);-- Search index (GIN index for full-text search)
CREATE INDEX idx_chapters_search ON chapters USING GIN(search_vector);-- Indexes for common queries
CREATE INDEX idx_documents_slug ON documents(slug);
CREATE INDEX idx_versions_document_id ON document_versions(document_id);
CREATE INDEX idx_versions_status ON document_versions(status);
CREATE INDEX idx_chapters_version_id ON chapters(version_id);

**Total tables: 3** (vs 10+ in pure database approach)
**Content storage: 0 bytes** (all in files)

## Component Responsibilities

### Backend Services

#### 1. FileStorageService (NEW)
**Purpose**: Manage file system operations

**Key Methods**:
```pythonclass FileStorageService:
def init(self, base_path: str = "storage/documents"):
self._base_path = Path(base_path)def save_chapter(
    self,
    doc_slug: str,
    version: str,
    chapter_num: int,
    content: str
) -> str:
    """Save chapter markdown to file, return file path."""def read_chapter(self, file_path: str) -> str:
    """Read chapter content from file."""def save_metadata(
    self,
    doc_slug: str,
    version: str,
    metadata: dict
) -> str:
    """Save version metadata.json."""def read_metadata(self, metadata_path: str) -> dict:
    """Read metadata.json."""def save_linked_doc(
    self,
    doc_slug: str,
    version: str,
    filename: str,
    content: str
) -> str:
    """Save linked explanation document."""def list_chapters(
    self,
    doc_slug: str,
    version: str
) -> List[str]:
    """List all chapter files for a version."""def get_active_version(self, doc_slug: str) -> str:
    """Read active_version.txt."""def set_active_version(
    self,
    doc_slug: str,
    version: str
) -> None:
    """Write active_version.txt."""def copy_version(
    self,
    doc_slug: str,
    from_version: str,
    to_version: str
) -> None:
    """Copy entire version directory."""

#### 2. DocumentProcessor (UPDATED)
**Purpose**: Orchestrate JSON → Markdown → File System

**Flow**:
```python
Receive Docling JSON
Call RichMarkdownGenerator.generate_chapters()
For each chapter:

Save markdown to file via FileStorageService
Extract metadata (title, page range, word count)
Create chapter record in DB (metadata only)
Generate search index from file content


Save version metadata.json
Create document_version record in DB
Update search indexes


#### 3. SearchService (UPDATED - Hybrid)
**Purpose**: Search using DB index, load results from files

**Flow**:
```python
Query PostgreSQL search_vector index
Get matching chapter IDs and file paths
Load chapter content from files
Extract snippets around matches
Return results with content + metadata


**Key Methods**:
```pythonclass SearchService:
async def search(
self,
document_id: UUID,
query: str,
limit: int = 20
) -> List[SearchResult]:
"""
Search chapters using DB index, load content from files.
"""
# 1. Search DB index
results = await self._db.execute("""
SELECT c.id, c.title, c.file_path, c.page_range,
ts_rank(c.search_vector, plainto_tsquery('english', :query)) as rank
FROM chapters c
JOIN document_versions dv ON c.version_id = dv.id
WHERE dv.document_id = :doc_id
AND c.search_vector @@ plainto_tsquery('english', :query)
ORDER BY rank DESC
LIMIT :limit
""", {"doc_id": document_id, "query": query, "limit": limit})    # 2. Load content from files and extract snippets
    search_results = []
    for row in results:
        content = self._file_storage.read_chapter(row.file_path)
        snippet = self._extract_snippet(content, query)        search_results.append(SearchResult(
            chapter_id=row.id,
            title=row.title,
            page_range=row.page_range,
            snippet=snippet,
            relevance_score=row.rank
        ))    return search_resultsasync def update_search_index(
    self,
    chapter_id: UUID,
    file_path: str
) -> None:
    """
    Read chapter file and update search_vector in DB.
    """
    content = self._file_storage.read_chapter(file_path)    # Generate search vector
    await self._db.execute("""
        UPDATE chapters
        SET search_vector = to_tsvector('english', :content)
        WHERE id = :chapter_id
    """, {"chapter_id": chapter_id, "content": content})

#### 4. RichMarkdownGenerator (UNCHANGED)
See existing documentation - still generates rich markdown from Docling JSON.

#### 5. TOCGenerator (UPDATED - File-Based)
**Purpose**: Generate TOC by parsing markdown files

**Flow**:
```python
Load all chapter files for version
Parse each file to extract headings
Build hierarchical TOC structure
Return TOC tree


## API Endpoints (UPDATED)

### Document Management

#### Upload DocumentPOST /api/documents/upload

**Request**:Content-Type: multipart/form-datafile: <docling-json-file>
title: "NSE NNF Protocol"
version: "6.3"
file_type: "json"

**Response**:
```json{
"id": "uuid",
"slug": "nse-nnf-protocol",
"title": "NSE NNF Protocol",
"version": "6.3",
"status": "processing"
}

#### Get Document ContentGET /api/documents/{doc_id}/chapters/{chapter_num}

**Response**:
```json{
"chapter_number": 4,
"title": "Order and Trade Management",
"content": "# Chapter 4...",
"page_range": "46-72",
"has_manual_content": true,
"has_linked_docs": true,
"metadata": {
"version": "6.3",
"word_count": 5840
}
}

#### Get Linked DocumentGET /api/documents/{doc_id}/links/{filename}

**Response**:
```json{
"filename": "chapter-04-order-types-clarification.md",
"title": "Order Types Clarification",
"content": "# Order Types Clarification...",
"linked_to": ["chapter-04-order-entry", "chapter-04-order-modification"],
"author": "product-manager@example.com",
"created_at": "2025-01-15T10:30:00Z"
}

### SearchGET /api/documents/{doc_id}/search?q=BOARD_LOT_IN&limit=20

**Response**:
```json{
"query": "BOARD_LOT_IN",
"total_results": 5,
"results": [
{
"chapter_id": "uuid",
"chapter_number": 4,
"title": "Order Entry",
"page_range": "46-72",
"snippet": "The transaction code is <mark>BOARD_LOT_IN</mark> (2000)...",
"relevance_score": 0.95
}
]
}

## Performance Characteristics

| Operation | File-Based | Database-Only |
|-----------|------------|---------------|
| **Read Chapter** | ~5ms (file read) | ~3ms (DB query) |
| **Search** | ~50ms (DB index + file load) | ~30ms (DB only) |
| **Upload Document** | ~2s (convert + write files) | ~2s (convert + insert) |
| **List Documents** | ~2ms (DB metadata) | ~2ms (DB query) |
| **Generate TOC** | ~100ms (parse files) | ~50ms (DB query) |
| **Export Document** | ~10ms (zip files) | ~500ms (query + format) |

**Verdict**: File-based is fast enough for documentation use case (< 100ms for reads).

## Advantages of This Architecture

1. ✅ **Simple**: Content in files, metadata in DB
2. ✅ **Portable**: Zip and move entire document
3. ✅ **Debuggable**: Open files in any text editor
4. ✅ **Git-compatible**: Version control files directly
5. ✅ **LLM-ready**: Native markdown format for AI integration
6. ✅ **Backups**: Just copy directory
7. ✅ **Fast**: Database index for search, files for content
8. ✅ **Scalable**: Can add vector DB for semantic search later

## Future Enhancements

### Phase 2: Manual Edit Markers
- Add save dialog: "Content Update" vs "Manual Note"
- Parse and preserve `<!-- MANUAL -->` blocks

### Phase 3: Linked Documents
- UI to create linked explanation docs
- Store in `links/` directory

### Phase 4: Version Diff & Merge
- Generate line-by-line diffs
- Chapter-by-chapter review UI
- Merge with manual block preservation

### Phase 5: LLM Integration
- Conversational Q&A over documentation
- RAG (Retrieval Augmented Generation)
- Auto-generate annotations
- Explain version differences

See `.claude/PRD.md` for detailed feature descriptions.


## Annotations & Linking System (Obsidian-Style)

### Philosophy: Pure Markdown Wikilinks

All annotations, notes, and references are **just markdown files** with `[[wikilinks]]`. No complex database tracking - links are discovered by parsing markdown files.

### File Structure
```
backend/storage/documents/{doc-slug}/
  active_version.txt
  
  versions/
    v6.1/
      metadata.json
      
      chapters/                    # Auto-generated from Docling JSON
        chapter-01-introduction.md
        chapter-04-order-entry.md
        chapter-07-broadcast.md
        ...
      
      notes/                       # User's notes/annotations
        my-production-notes.md
        order-validation-tips.md
        team-discussion-20250115.md
        meeting-notes/             # User can organize in folders
          exchange-clarification.md
        ...
      
      references/                  # Detailed explanation docs
        order-types-guide.md
        error-handling-reference.md
        batch-processing-explained.md
        ...
```

### Wikilink Format
```markdown
# Chapter 4: Order Entry

The transaction code is BOARD_LOT_IN (2000).

See: [[order-validation-tips]] for production deployment notes.

Regular lot orders are explained in detail at [[order-types-guide]].

## Section 4.2: Order Modification

Link to specific section: [[chapter-07-broadcast#section-7-2]]
```

**Syntax**:
- `[[note-title]]` - Links to file `notes/note-title.md` or `references/note-title.md`
- `[[chapter-04-order-entry]]` - Links to chapter file
- `[[chapter-04#section-4-1]]` - Links to specific section (anchor)

### How Links are Discovered

Links are **NOT stored in database**. They are discovered by parsing markdown files:
```python
# Scan all markdown files
for file in glob("**/*.md"):
    content = open(file).read()
    
    # Find all [[wikilinks]]
    links = re.findall(r'\[\[([^\]]+)\]\]', content)
    
    # Build graph: file → links_to → other_files
    graph[file] = links
```

**Backlinks**: For any file, find all files that link to it by inverting the graph.

### Manual Edit Markers

When user edits a chapter and chooses "Save as Manual Note", content is wrapped with markers for preservation during version merges:
```markdown
# Chapter 4: Order Entry

The transaction code is BOARD_LOT_IN (2000).

<!-- MANUAL:START:john@example.com:2025-01-15:callout -->
> [!important] 💡
> **Production Note**: Always validate order quantity before submission.
> This prevents common integration errors in high-volume scenarios.
<!-- MANUAL:END -->

Regular lot orders are processed...
```

**Marker Types**:
- `callout` - Important callout (Obsidian-style)
- `note` - Simple note
- `warning` - Warning/caution
- `tip` - Helpful tip
- `code` - Code example

### User Document Types

| Type | Directory | Purpose | Example |
|------|-----------|---------|---------|
| **Note** | `notes/` | Personal notes, annotations, quick references | `my-production-notes.md` |
| **Reference** | `references/` | Detailed guides, explanations, how-tos | `order-types-guide.md` |
| **Chapter** | `chapters/` | Auto-generated main content (not editable directly) | `chapter-04-order-entry.md` |

**Note**: Users can organize notes/references in subfolders as they wish.

### Database Schema (Minimal)
```sql
-- Only for search indexing, NOT for link tracking
CREATE TABLE user_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    version VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,           -- "notes/order-validation-tips.md"
    title TEXT NOT NULL,
    doc_type VARCHAR(20) NOT NULL,             -- "note" or "reference"
    search_vector TSVECTOR,                    -- For full-text search
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    tags TEXT[]                                -- Optional tags
);

-- Index for search
CREATE INDEX idx_user_docs_search ON user_documents USING GIN(search_vector);
CREATE INDEX idx_user_docs_type ON user_documents(doc_type);
CREATE INDEX idx_user_docs_path ON user_documents(file_path);
```

**Key Point**: Database is ONLY for search indexing. Link relationships are discovered by parsing, not stored.

### Component Responsibilities

#### WikiLinkService (NEW)

**Purpose**: Parse wikilinks, resolve to file paths, build link graphs

**Key Methods**:
```python
class WikiLinkService:
    def parse_wikilinks(self, content: str) -> List[WikiLink]:
        """
        Extract all [[wikilinks]] from markdown content.
        Returns: List of WikiLink objects with target and optional anchor
        """
        
    def resolve_link(
        self, 
        link_text: str, 
        base_path: str
    ) -> Optional[str]:
        """
        Resolve [[order-validation-tips]] to actual file path.
        Searches in: notes/, references/, chapters/
        Returns: Full file path or None if not found
        """
        
    def get_backlinks(
        self,
        target_file: str,
        doc_path: str
    ) -> List[Backlink]:
        """
        Find all files that link to target_file.
        
        Process:
        1. Scan all markdown files in doc_path
        2. Parse wikilinks in each file
        3. Filter for links pointing to target_file
        4. Extract snippet around the link
        
        Returns: List of Backlink objects with source, snippet, line number
        """
        
    def build_link_graph(
        self,
        doc_path: str
    ) -> Dict[str, GraphNode]:
        """
        Build complete link graph for entire document.
        
        Returns: Dict mapping filename → GraphNode with:
        - links_to: List of outgoing links
        - linked_from: List of incoming links (backlinks)
        - file_type: "chapter", "note", "reference"
        """
```

#### UserDocumentService (NEW)

**Purpose**: Manage user-created notes and references

**Key Methods**:
```python
class UserDocumentService:
    def __init__(
        self,
        db: AsyncSession,
        file_storage: FileStorageService,
        wikilink_service: WikiLinkService
    ):
        self._db = db
        self._file_storage = file_storage
        self._wikilinks = wikilink_service
    
    async def create_note(
        self,
        doc_slug: str,
        version: str,
        title: str,
        content: str,
        doc_type: str = "note",
        created_by: str = None,
        tags: List[str] = None
    ) -> UserDocument:
        """
        Create new note or reference document.
        
        Flow:
        1. Generate filename from title (slugified)
        2. Save to notes/ or references/ directory
        3. Create DB record for search indexing
        4. Generate search_vector from content
        5. Return UserDocument object
        """
        
    async def update_document(
        self,
        file_path: str,
        content: str
    ) -> None:
        """
        Update note/reference content.
        
        Flow:
        1. Save to file
        2. Update search_vector in DB
        3. Update updated_at timestamp
        """
        
    async def read_document(
        self,
        file_path: str
    ) -> str:
        """Read note/reference content from file."""
        
    async def list_documents(
        self,
        doc_slug: str,
        version: str,
        doc_type: Optional[str] = None
    ) -> List[UserDocument]:
        """
        List all notes/references for version.
        Optionally filter by doc_type ("note" or "reference")
        """
        
    async def delete_document(
        self,
        file_path: str
    ) -> None:
        """
        Delete note/reference.
        
        Flow:
        1. Delete file
        2. Delete DB record
        """
        
    async def move_document(
        self,
        old_path: str,
        new_path: str
    ) -> None:
        """
        Rename/move note/reference.
        
        Flow:
        1. Move file
        2. Update file_path in DB
        
        Note: Wikilinks pointing to old name will need updating
        (can be done manually or with find-replace)
        """
```

#### ChapterRenderService (UPDATED)

**Purpose**: Render chapters with resolved wikilinks and backlinks

**Key Methods**:
```python
class ChapterRenderService:
    def __init__(
        self,
        file_storage: FileStorageService,
        wikilink_service: WikiLinkService
    ):
        self._file_storage = file_storage
        self._wikilinks = wikilink_service
    
    async def render_chapter(
        self,
        chapter_file_path: str,
        include_backlinks: bool = True,
        resolve_links: bool = True
    ) -> ChapterWithLinks:
        """
        Render chapter with all link information.
        
        Returns:
        - content: Original markdown (optionally with resolved links)
        - backlinks: List of files linking to this chapter
        - outline: TOC extracted from headings
        - metadata: Frontmatter data
        """
        
    def resolve_wikilinks_to_urls(
        self,
        content: str,
        base_path: str
    ) -> str:
        """
        Convert [[wikilinks]] to markdown links for rendering.
        
        Example:
        [[order-validation-tips]] 
        → 
        [order-validation-tips](/api/documents/nse-nnf/notes/order-validation-tips)
        
        [[chapter-04#section-4-1]]
        →
        [Chapter 4, Section 4.1](/api/documents/nse-nnf/chapters/4#section-4-1)
        """
```

### API Endpoints

#### User Documents (Notes/References)
```
POST   /api/documents/{doc_id}/versions/{version}/notes
GET    /api/documents/{doc_id}/versions/{version}/notes
GET    /api/documents/{doc_id}/versions/{version}/notes/{filename}
PUT    /api/documents/{doc_id}/versions/{version}/notes/{filename}
DELETE /api/documents/{doc_id}/versions/{version}/notes/{filename}
POST   /api/documents/{doc_id}/versions/{version}/notes/{filename}/move
```

**Example - Create Note**:

Request:
```json
POST /api/documents/nse-nnf-protocol/versions/v6.1/notes

{
  "title": "Order Validation Tips",
  "content": "# Order Validation Tips\n\n...",
  "doc_type": "note",
  "tags": ["production", "critical"],
  "link_to_source": {
    "chapter": "chapter-04-order-entry",
    "insert_link": true
  }
}
```

Response:
```json
{
  "id": "uuid",
  "file_path": "notes/order-validation-tips.md",
  "title": "Order Validation Tips",
  "doc_type": "note",
  "created_at": "2025-01-15T10:30:00Z",
  "link_inserted": true
}
```

#### Wikilinks & Backlinks
```
GET    /api/documents/{doc_id}/versions/{version}/backlinks/{filename}
GET    /api/documents/{doc_id}/versions/{version}/graph
POST   /api/documents/{doc_id}/versions/{version}/resolve-link
GET    /api/documents/{doc_id}/versions/{version}/search-linkable
```

**Example - Get Backlinks**:

Request:
```
GET /api/documents/nse-nnf-protocol/versions/v6.1/backlinks/chapter-04-order-entry.md
```

Response:
```json
{
  "target_file": "chapters/chapter-04-order-entry.md",
  "target_title": "Chapter 4: Order Entry",
  "backlinks": [
    {
      "source_file": "notes/order-validation-tips.md",
      "source_title": "Order Validation Tips",
      "snippet": "From [[chapter-04-order-entry#section-4-1]]:\n> The transaction code...",
      "line_number": 5
    },
    {
      "source_file": "notes/my-production-notes.md",
      "source_title": "My Production Notes",
      "snippet": "Review order entry process at [[chapter-04-order-entry]]",
      "line_number": 12
    }
  ],
  "total_backlinks": 2
}
```

**Example - Link Graph**:

Request:
```
GET /api/documents/nse-nnf-protocol/versions/v6.1/graph
```

Response:
```json
{
  "nodes": [
    {
      "id": "chapter-04-order-entry",
      "title": "Chapter 4: Order Entry",
      "type": "chapter",
      "file_path": "chapters/chapter-04-order-entry.md"
    },
    {
      "id": "order-validation-tips",
      "title": "Order Validation Tips",
      "type": "note",
      "file_path": "notes/order-validation-tips.md"
    }
  ],
  "edges": [
    {
      "from": "order-validation-tips",
      "to": "chapter-04-order-entry",
      "anchor": "section-4-1"
    },
    {
      "from": "chapter-04-order-entry",
      "to": "order-validation-tips",
      "anchor": null
    }
  ]
}
```

#### Chapter Rendering (UPDATED)
```
GET    /api/documents/{doc_id}/chapters/{chapter_id}?include_backlinks=true&resolve_links=true
```

Response:
```json
{
  "chapter_number": 4,
  "title": "Order and Trade Management",
  "content": "# Chapter 4...\n\nSee: [[order-validation-tips]]",
  "content_with_resolved_links": "# Chapter 4...\n\nSee: [order-validation-tips](/api/documents/.../notes/order-validation-tips)",
  "backlinks": [
    {
      "source_file": "notes/order-validation-tips.md",
      "source_title": "Order Validation Tips",
      "snippet": "...",
      "line_number": 5
    }
  ],
  "outline": [
    {"level": 1, "text": "Chapter 4: Order Entry", "anchor": "chapter-4"},
    {"level": 2, "text": "Section 4.1", "anchor": "section-4-1"}
  ]
}
```

### User Workflows

#### Workflow 1: Create Note from Chapter
```
User Action: Selects text in Chapter 4 → Right-click → "Create Note"

Flow:
1. Dialog opens:
   - Note title: [Auto-filled or edit]
   - Note type: ● Note  ○ Reference
   - Link back: ☑ Insert [[note-title]] in chapter
   
2. User clicks "Create & Edit"

3. System creates:
   - File: notes/order-validation-tips.md
   - Template with context from selection
   - DB record for search

4. If "Link back" checked:
   - Inserts [[order-validation-tips]] at cursor position in chapter
   
5. Opens markdown editor for user to write content
```

#### Workflow 2: Link to Existing Note
```
User Action: Types in chapter: "See: [[order-va"

Flow:
1. Autocomplete triggers after "[["

2. Dropdown shows matching files:
   - [[order-validation-tips]]
   - [[order-types-guide]]

3. User selects → Link inserted

4. On chapter view, link is clickable

5. Backlinks automatically appear in both directions
```

#### Workflow 3: Edit Chapter with Manual Marker
```
User Action: Edits Chapter 4 content → Clicks "Save"

Flow:
1. Dialog appears:
   ┌─────────────────────────────────┐
   │ Save Changes                    │
   ├─────────────────────────────────┤
   │ ● Direct Edit                   │
   │   Updates chapter content       │
   │                                 │
   │ ○ Manual Note (Preserved)      │
   │   Marked for version merge      │
   │                                 │
   │ If Manual Note:                 │
   │ Marker type:                    │
   │ ○ Callout  ○ Note  ○ Warning   │
   └─────────────────────────────────┘

2. If "Direct Edit": Save to file normally

3. If "Manual Note":
   - Wrap edited content with:
     <!-- MANUAL:START:user:date:type -->
     [edited content]
     <!-- MANUAL:END -->
   - This will be preserved during version merges
```

#### Workflow 4: Promote Note to Reference
```
User Action: Has a note that's grown into a guide

Flow:
1. User opens note: notes/order-validation-tips.md

2. User clicks "Convert to Reference"

3. Dialog:
   ┌─────────────────────────────────┐
   │ Convert to Reference Document   │
   ├─────────────────────────────────┤
   │ New location:                   │
   │ references/order-validation-guide.md
   │                                 │
   │ Update all [[wikilinks]]?       │
   │ ☑ Yes, update 3 references      │
   │                                 │
   │ [Cancel] [Convert]              │
   └─────────────────────────────────┘

4. System:
   - Moves file notes/ → references/
   - Updates file_path in DB
   - If checked: Updates all [[old-name]] → [[new-name]]
```

### Frontend Components

#### WikiLinkEditor Component

**Features**:
- Markdown editor with wikilink support
- Autocomplete after typing `[[`
- Syntax highlighting for `[[wikilinks]]`
- Click wikilink to navigate

**Libraries**:
- React-based markdown editor (e.g., CodeMirror or Monaco)
- Custom autocomplete plugin for wikilinks

#### BacklinksPanel Component

**Features**:
- Right sidebar showing "What links here?"
- List of all documents linking to current doc
- Click to navigate to source
- Show snippet with context

**UI**:
```
┌─────────────────────────────┐
│ 📝 Linked References (3)   │
├─────────────────────────────┤
│ 📄 order-validation-tips    │
│   "From [[chapter-04]]..."  │
│   [View Note]               │
│                             │
│ 📄 my-production-notes      │
│   "Review [[chapter-04]]"   │
│   [View Note]               │
└─────────────────────────────┘
```

#### SaveEditDialog Component

**Features**:
- Radio buttons: Direct Edit vs Manual Note
- If Manual Note: dropdown for marker type
- Preview of how edit will appear

#### GraphView Component (Optional - Phase 2)

**Features**:
- Visual graph of document connections
- Nodes = chapters + notes + references
- Edges = wikilinks
- Interactive: click node to navigate
- Filter by type (chapters only, notes only)

**Libraries**:
- D3.js or react-force-graph
- Zoom/pan controls

### Performance Considerations

#### Link Discovery Performance

**Challenge**: Parsing all markdown files on every request is slow.

**Solution**: Cache link graph in memory, rebuild periodically.
```python
class LinkGraphCache:
    def __init__(self):
        self._cache = {}
        self._last_updated = {}
    
    async def get_graph(self, doc_path: str) -> LinkGraph:
        """
        Get cached graph or rebuild if stale.
        
        Rebuild triggers:
        - Cache miss
        - File modified since last cache
        - Manual invalidation
        """
        if self._is_stale(doc_path):
            self._cache[doc_path] = self._build_graph(doc_path)
            self._last_updated[doc_path] = time.time()
        
        return self._cache[doc_path]
```

**Cache Invalidation**:
- When note/reference created/updated/deleted
- When chapter edited (if contains new wikilinks)
- Can also use file system watchers for automatic invalidation

#### Search Performance

**Use PostgreSQL full-text search** for notes/references:
```sql
-- Index search_vector column
CREATE INDEX idx_user_docs_search ON user_documents USING GIN(search_vector);

-- Search query
SELECT * FROM user_documents
WHERE search_vector @@ plainto_tsquery('english', 'order validation')
ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'order validation')) DESC;
```

### Future Enhancements (Phase 2+)

1. **Graph Visualization**: Interactive link graph view
2. **Smart Rename**: Update all wikilinks when renaming a note
3. **Broken Link Detection**: Find and highlight `[[links]]` pointing to non-existent files
4. **Link Suggestions**: AI-powered suggestions for relevant links while writing
5. **Bidirectional Sync**: Two-way sync with external Obsidian vault
6. **Templates**: Note templates for common use cases
7. **Tags View**: Browse documents by tags
8. **Daily Notes**: Auto-create daily note files

### Advantages of This Approach

1. ✅ **Simple**: Pure markdown files with wikilinks
2. ✅ **Portable**: Export as zip, works in Obsidian
3. ✅ **Flexible**: User organizes notes as they wish
4. ✅ **No Vendor Lock-in**: Standard markdown format
5. ✅ **Git-friendly**: Can version control entire document
6. ✅ **LLM-ready**: Native format for AI integration
7. ✅ **Discoverable**: Links found by parsing, not DB joins
8. ✅ **Scalable**: Cache graph for performance