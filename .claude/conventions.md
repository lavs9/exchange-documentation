# Coding Conventions & Standards

## General Principles
1. **Readability over cleverness**: Clear code > clever code
2. **Type safety**: Use type hints (Python) and TypeScript strictly
3. **DRY but not obsessive**: Repeat twice before abstracting
4. **Test coverage**: Aim for 70%+ in Phase 1
5. **Documentation**: Docstrings for all public methods

## Python (Backend) Conventions

### Code Style
- **Formatter**: Black (line length: 88)
- **Linter**: Ruff (replaces flake8, isort, pylint)
- **Type Checker**: mypy (strict mode)

### File Naming
- Snake case: `document_processor.py`, `search_service.py`
- Test files: `test_document_processor.py`

### Import Order
```python
# 1. Standard library
import os
from datetime import datetime
from typing import List, Optional

# 2. Third-party
from fastapi import FastAPI, UploadFile
from sqlalchemy import select

# 3. Local
from app.models.document import Document
from app.services.pdf_parser import PDFParser
Function/Method Signatures
pythondef process_document(
    file: UploadFile,
    metadata: Optional[Dict[str, Any]] = None
) -> Document:
    """
    Process uploaded PDF and create document record.
    
    Args:
        file: Uploaded PDF file
        metadata: Optional metadata dictionary
        
    Returns:
        Created Document instance
        
    Raises:
        DocumentProcessingError: If PDF parsing fails
    """
    pass
Class Structure
pythonclass DocumentProcessor:
    """Orchestrates PDF to structured document conversion."""
    
    def __init__(
        self,
        parser: PDFParser,
        db_session: AsyncSession
    ) -> None:
        self._parser = parser
        self._db = db_session
        
    async def process(self, file: UploadFile) -> Document:
        """Process document (public interface)."""
        pass
        
    async def _save_sections(self, sections: List[Section]) -> None:
        """Save sections to database (private helper)."""
        pass
Error Handling
python# Custom exceptions
class DocumentProcessingError(Exception):
    """Raised when document processing fails."""
    pass

# Usage
try:
    sections = await parser.parse_pdf(file_path)
except DoclingError as e:
    logger.error(f"Docling parsing failed: {e}", exc_info=True)
    raise DocumentProcessingError(f"Failed to parse PDF: {str(e)}") from e
Async/Await
python# Use async for I/O operations
async def create_document(db: AsyncSession, doc: DocumentCreate) -> Document:
    db_doc = Document(**doc.dict())
    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)
    return db_doc

# Sync for CPU-bound operations
def parse_markdown_structure(markdown: str) -> List[Section]:
    # Heavy processing
    return sections
Configuration
python# Use Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    upload_dir: Path = Path("uploads")
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    
    class Config:
        env_file = ".env"
        
settings = Settings()
Logging
pythonimport logging

logger = logging.getLogger(__name__)

# Usage
logger.info("Processing document", extra={"document_id": doc.id})
logger.error("Failed to parse PDF", exc_info=True)
TypeScript (Frontend) Conventions
Code Style

Formatter: Prettier
Linter: ESLint (Airbnb config + TypeScript)

File Naming

Components: PascalCase: DocumentViewer.tsx, TableOfContents.tsx
Utilities: camelCase: apiClient.ts, formatters.ts
Types: PascalCase: Document.ts, SearchResult.ts

Component Structure
typescript// Functional component with TypeScript
interface DocumentViewerProps {
  documentId: string;
  onSectionClick?: (sectionId: string) => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ 
  documentId, 
  onSectionClick 
}) => {
  // Hooks at top
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadDocument();
  }, [documentId]);
  
  // Helper functions
  const loadDocument = async () => {
    // ...
  };
  
  // Early returns for loading/error states
  if (loading) return <LoadingSpinner />;
  if (!content) return <EmptyState />;
  
  // Main render
  return (
    <div className="document-viewer">
      {/* ... */}
    </div>
  );
};
Type Definitions
typescript// types/document.ts
export interface Document {
  id: string;
  title: string;
  version: string;
  uploadDate: Date;
  pageCount: number;
  status: DocumentStatus;
}

export type DocumentStatus = 'processing' | 'completed' | 'failed';

export interface Section {
  id: string;
  level: number;
  title: string;
  content: string;
  pageNumber: number;
  parentId?: string;
  children: string[];
}

// Use enums sparingly, prefer union types
export type SearchFilter = 'all' | 'chapter' | 'section';
API Client
typescript// services/api.ts
import axios, { AxiosInstance } from 'axios';

class ApiClient {
  private client: AxiosInstance;
  
  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    });
  }
  
  async uploadDocument(file: File, metadata: DocumentMetadata): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', metadata.title);
    formData.append('version', metadata.version);
    
    const response = await this.client.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    return response.data;
  }
  
  async searchDocument(
    documentId: string, 
    query: string, 
    page: number = 1
  ): Promise<SearchResults> {
    const response = await this.client.get<SearchResults>(
      `/documents/${documentId}/search`,
      { params: { q: query, page } }
    );
    
    return response.data;
  }
}

export const apiClient = new ApiClient(import.meta.env.VITE_API_URL);
State Management
typescript// Use React Context for simple state
interface AppContextType {
  currentDocument: Document | null;
  setCurrentDocument: (doc: Document | null) => void;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);

// Custom hook
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
Error Handling
typescript// Custom error types
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Usage in component
const [error, setError] = useState<string | null>(null);

try {
  await apiClient.uploadDocument(file, metadata);
} catch (err) {
  if (err instanceof ApiError) {
    setError(`Upload failed: ${err.message}`);
  } else {
    setError('An unexpected error occurred');
  }
  console.error('Upload error:', err);
}
Git Conventions
Branch Naming

Feature: feature/pdf-parsing
Bug fix: fix/search-highlighting
Refactor: refactor/api-structure
Documentation: docs/api-examples

Commit Messages
Follow Conventional Commits:
<type>(<scope>): <subject>

<body>

<footer>
Types: feat, fix, docs, style, refactor, test, chore
Examples:
feat(backend): add PDF parsing with docling

- Integrate docling library
- Extract sections with hierarchy
- Handle tables and code blocks

Closes #12

fix(frontend): correct TOC scroll behavior

- Use intersection observer instead of scroll event
- Debounce active section updates

test(search): add full-text search integration tests
Testing Conventions
Python Tests (pytest)
python# tests/test_document_processor.py
import pytest
from app.services.document_processor import DocumentProcessor

@pytest.fixture
def processor(db_session):
    return DocumentProcessor(db_session)

class TestDocumentProcessor:
    """Test suite for DocumentProcessor."""
    
    async def test_process_valid_pdf(self, processor, sample_pdf):
        """Should successfully process valid NSE PDF."""
        result = await processor.process(sample_pdf)
        
        assert result.status == "completed"
        assert result.page_count > 0
        assert len(result.sections) > 10
        
    async def test_process_invalid_pdf_raises_error(self, processor):
        """Should raise DocumentProcessingError for invalid PDF."""
        with pytest.raises(DocumentProcessingError):
            await processor.process(corrupted_pdf)
TypeScript Tests (Vitest + React Testing Library)
typescript// components/DocumentViewer.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { DocumentViewer } from './DocumentViewer';

describe('DocumentViewer', () => {
  it('renders loading state initially', () => {
    render(<DocumentViewer documentId="123" />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
  
  it('displays document content after loading', async () => {
    render(<DocumentViewer documentId="123" />);
    
    await waitFor(() => {
      expect(screen.getByText(/Chapter 1/)).toBeInTheDocument();
    });
  });
});
Documentation Standards
README.md Structure
markdown# Project Name

Brief description

## Features
- Feature 1
- Feature 2

## Quick Start
```bash
docker-compose up
Development
...
Testing
...
Architecture
See .claude/architecture.md

### API Documentation
- Use FastAPI's automatic OpenAPI generation
- Add detailed descriptions to path operations:
```python
@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    title: str = Form(..., description="Document title"),
    version: str = Form(..., description="Document version (e.g., 'v6.2')"),
) -> DocumentResponse:
    """
    Upload and process a new document.
    
    This endpoint:
    1. Validates the uploaded file
    2. Extracts content using Docling
    3. Generates table of contents
    4. Stores in database
    
    Returns the created document with processing status.
    """
    pass
File Organization
Backend Structure
backend/app/
├── api/
│   ├── __init__.py
│   ├── dependencies.py      # Shared dependencies (DB session, etc.)
│   ├── documents.py          # Document management endpoints
│   └── search.py             # Search endpoints
├── core/
│   ├── __init__.py
│   ├── config.py             # Settings
│   └── database.py           # DB connection
├── models/
│   ├── __init__.py
│   ├── document.py           # SQLAlchemy models
│   └── section.py
├── schemas/
│   ├── __init__.py
│   ├── document.py           # Pydantic schemas
│   └── search.py
├── services/
│   ├── __init__.py
│   ├── document_processor.py # Main processing logic
│   ├── pdf_parser.py         # Docling wrapper
│   ├── search_service.py     # Search logic
│   └── toc_generator.py      # TOC building
└── main.py                   # FastAPI app
Frontend Structure
frontend/src/
├── components/
│   ├── common/               # Shared components
│   │   ├── Button.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorMessage.tsx
│   ├── DocumentList.tsx
│   ├── DocumentViewer.tsx
│   ├── TableOfContents.tsx
│   └── SearchBar.tsx
├── services/
│   └── api.ts                # API client
├── types/
│   ├── document.ts
│   └── search.ts
├── hooks/
│   └── useDebounce.ts        # Custom hooks
├── utils/
│   └── formatters.ts         # Utility functions
├── App.tsx
└── main.tsx
Performance Guidelines
Backend

Use async/await for all I/O operations
Implement pagination for list endpoints (default: 20 items)
Use database connection pooling (SQLAlchemy default: 5-10)
Add database indexes for frequently queried fields

Frontend

Lazy load components with React.lazy()
Debounce search input (300ms)
Use React.memo for expensive components (TOC entries)
Implement virtual scrolling if documents > 1000 sections (future)

Security Checklist
Backend

 Validate file uploads (MIME type, size)
 Sanitize user input (SQL injection protection via ORM)
 Use parameterized queries
 Implement rate limiting (future)
 Add CORS restrictions

Frontend

 Sanitize markdown output (react-markdown handles this)
 Validate user input before API calls
 Handle errors gracefully without exposing internals
 Use HTTPS in production (future)

Accessibility (A11y)
Frontend

Use semantic HTML (<nav>, <main>, <article>)
Add ARIA labels where needed
Ensure keyboard navigation works
Maintain color contrast ratios (WCAG AA)
Add focus indicators

typescript// Good
<button 
  onClick={handleClick}
  aria-label="Upload document"
  className="focus:ring-2 focus:ring-blue-500"
>
  Upload
</button>

// Bad
<div onClick={handleClick}>Upload</div>