# Documentation Prompt Template

When writing/updating documentation, provide:

## Documentation Type
- [ ] API endpoint documentation
- [ ] Component documentation
- [ ] Architecture documentation
- [ ] User guide
- [ ] Setup/deployment guide
- [ ] Troubleshooting guide
- [ ] Code comments/docstrings

## Target Audience
- [ ] Developers (technical)
- [ ] End users (non-technical)
- [ ] DevOps/Infrastructure
- [ ] Product managers
- [ ] New team members

## Content to Document
- Feature/Component: [Name]
- Location: [File path or URL]
- Key concepts: [List main concepts]
- Examples needed: [Yes/No]

## Documentation Requirements
- [ ] Clear, concise language
- [ ] Code examples where applicable
- [ ] Diagrams/screenshots if needed
- [ ] Links to related documentation
- [ ] Step-by-step instructions (if applicable)
- [ ] Common pitfalls/gotchas highlighted

## Format
- [ ] Markdown file
- [ ] Inline code comments
- [ ] OpenAPI/Swagger spec
- [ ] README section
- [ ] Wiki page
- [ ] Docstring

## Current State
[Paste existing documentation if updating, or write "New documentation"]

## Desired Content Outline

Overview/Introduction
Prerequisites (if applicable)
Main content
3.1. Sub-section 1
3.2. Sub-section 2
Examples
Troubleshooting (if applicable)
Related resources


---

## Examples by Documentation Type

### 1. API Endpoint Documentation

**Template:**
```markdown
## Endpoint: [METHOD] /api/path

### Description
[Brief description of what this endpoint does]

### Request
- **Method**: GET/POST/PUT/DELETE
- **URL**: `/api/documents/{id}/search`
- **Authentication**: [Required/Not required]

#### URL Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id        | UUID | Yes      | Document ID |

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| q         | string | Yes    | -       | Search query |
| page      | int  | No       | 1       | Page number |
| limit     | int  | No       | 20      | Results per page |

#### Request Body
```json
{
  "field": "value"
}
Response
Success Response (200 OK)
json{
  "query": "BOARD_LOT_IN",
  "total_results": 23,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "section_id": "uuid",
      "section_title": "Chapter 4 - Order Entry",
      "page_number": 46,
      "snippet": "...transaction code is BOARD_LOT_IN...",
      "match_score": 0.95
    }
  ]
}
Error Responses

400 Bad Request: Invalid query parameter
404 Not Found: Document not found
500 Internal Server Error: Server error

Example Usage
cURL
bashcurl "http://localhost:8000/api/documents/123e4567-e89b-12d3-a456-426614174000/search?q=BOARD_LOT_IN&page=1&limit=10"
Python
pythonresponse = await client.get(
    f"/api/documents/{doc_id}/search",
    params={"q": "BOARD_LOT_IN", "page": 1, "limit": 10}
)
TypeScript
typescriptconst results = await apiClient.searchDocument(
  documentId,
  "BOARD_LOT_IN",
  1
);
Notes

Search is case-insensitive
Results are ranked by relevance
Maximum limit is 100


---

### 2. Component Documentation

**Template:**
```markdown
## Component: [ComponentName]

### Overview
[Brief description of what this component does and when to use it]

### Location
`src/components/[ComponentName].tsx`

### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| documentId | string | Yes | - | ID of document to display |
| onSectionClick | (sectionId: string) => void | No | undefined | Callback when section clicked |
| className | string | No | '' | Additional CSS classes |

### Usage

#### Basic Usage
```tsx
import { DocumentViewer } from '@/components/DocumentViewer';

function App() {
  return (
    <DocumentViewer 
      documentId="123e4567-e89b-12d3-a456-426614174000"
    />
  );
}
With Event Handler
tsx<DocumentViewer 
  documentId={docId}
  onSectionClick={(sectionId) => {
    console.log('Section clicked:', sectionId);
    // Navigate or perform action
  }}
/>
State Management

loading: Boolean indicating if content is loading
content: String containing markdown content
error: String containing error message (if any)

Dependencies

react-markdown: For markdown rendering
react-syntax-highlighter: For code block highlighting

Styling
Uses Tailwind CSS classes. Can be customized via className prop.
Testing
tsximport { render, screen } from '@testing-library/react';
import { DocumentViewer } from './DocumentViewer';

test('renders loading state', () => {
  render(<DocumentViewer documentId="123" />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});
Known Issues

Large documents (>1000 sections) may cause performance issues
Tables with many columns may overflow on mobile

Related Components

TableOfContents: For navigation
SearchBar: For searching within document


---

### 3. Architecture Documentation

**Template:**
```markdown
## Architecture: [System/Feature Name]

### Overview
[High-level description of the system/feature]

### Components

#### Component 1: [Name]
- **Purpose**: [What it does]
- **Technology**: [Tech used]
- **Key responsibilities**:
  - Responsibility 1
  - Responsibility 2

#### Component 2: [Name]
- **Purpose**: [What it does]
- **Technology**: [Tech used]
- **Key responsibilities**:
  - Responsibility 1
  - Responsibility 2

### Data Flow
User Action
↓
Frontend Component
↓
API Layer (REST)
↓
Service Layer
↓
Database
↓
Response back to User

### Sequence Diagram
[Optional: Include mermaid diagram or ASCII diagram]

### Database Schema

#### Table: documents
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    ...
);
API Contracts

See API Documentation

Technology Decisions
Why [Technology X]?

Reason 1
Reason 2
Reason 3

Alternatives Considered

Alternative 1: [Why not chosen]
Alternative 2: [Why not chosen]

Performance Considerations

Consideration 1
Consideration 2

Security Considerations

Security measure 1
Security measure 2

Future Improvements

Improvement 1
Improvement 2


---

### 4. User Guide Documentation

**Template:**
```markdown
## User Guide: [Feature Name]

### What is [Feature]?
[Simple explanation for non-technical users]

### Prerequisites
- Prerequisite 1
- Prerequisite 2

### Step-by-Step Instructions

#### Step 1: [Action]
1. Navigate to [location]
2. Click on [button/link]
3. [Result/What you should see]

**Screenshot:**
![Step 1](path/to/screenshot.png)

#### Step 2: [Action]
1. [Action description]
2. [Expected result]

**Screenshot:**
![Step 2](path/to/screenshot.png)

### Tips & Best Practices
- 💡 **Tip 1**: [Helpful tip]
- 💡 **Tip 2**: [Helpful tip]

### Common Problems

#### Problem 1: [Issue description]
**Solution**: [How to fix]

#### Problem 2: [Issue description]
**Solution**: [How to fix]

### FAQ

**Q: [Question]?**
A: [Answer]

**Q: [Question]?**
A: [Answer]

### Getting Help
If you encounter issues:
1. Check [Troubleshooting Guide](link)
2. Contact support at [email/link]

5. Setup/Deployment Documentation
Template:
markdown## Setup Guide: [System Name]

### Prerequisites

#### Required Software
- Docker v20.10+
- Docker Compose v2.0+
- Git

#### System Requirements
- OS: Linux/macOS/Windows with WSL2
- RAM: 8GB minimum
- Disk: 10GB free space

### Installation Steps

#### 1. Clone Repository
```bash
git clone [repository-url]
cd [project-directory]
2. Environment Configuration
bash# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your settings
3. Start Services
bashdocker-compose up -d
4. Verify Installation
bash# Check backend
curl http://localhost:8000/health

# Check frontend
# Open browser: http://localhost:3000
Configuration Options
Backend Environment Variables
VariableDescriptionDefaultRequiredDATABASE_URLPostgreSQL connection string-YesUPLOAD_DIRDirectory for uploaded files/app/uploadsNoMAX_UPLOAD_SIZE_MBMaximum file size50No
Frontend Environment Variables
VariableDescriptionDefaultRequiredVITE_API_URLBackend API URLhttp://localhost:8000Yes
Troubleshooting
Port Conflicts
bash# Check what's using port 8000
lsof -i :8000

# Solution: Stop conflicting service or change port in docker-compose.yml
Database Connection Errors
bash# Reset database
docker-compose down -v
docker-compose up -d postgres
Next Steps

Load sample data
Read user guide
Review API documentation


---

### 6. Code Comments/Docstrings

**Python Template:**
```python
def process_document(
    file: UploadFile,
    metadata: Optional[Dict[str, Any]] = None
) -> Document:
    """
    Process uploaded PDF and create document record.
    
    This function performs the following steps:
    1. Validates the uploaded file
    2. Extracts content using Docling
    3. Generates table of contents
    4. Stores sections in database
    
    Args:
        file: Uploaded PDF file from FastAPI UploadFile
        metadata: Optional metadata dictionary containing:
            - custom_field1: Description
            - custom_field2: Description
        
    Returns:
        Document: Created document instance with:
            - id: UUID of created document
            - status: Processing status
            - sections: List of extracted sections
        
    Raises:
        DocumentProcessingError: If PDF parsing fails
        ValueError: If file is not a valid PDF
        
    Example:
        >>> file = UploadFile(filename="doc.pdf")
        >>> doc = await process_document(file)
        >>> print(doc.id)
        '123e4567-e89b-12d3-a456-426614174000'
        
    Note:
        Processing time depends on document size.
        Large documents (>100 pages) may take several minutes.
    """
    pass
TypeScript Template:
typescript/**
 * Searches for documents matching the query
 * 
 * @param documentId - UUID of the document to search
 * @param query - Search query string
 * @param page - Page number (1-indexed)
 * @returns Promise resolving to search results
 * 
 * @throws {ApiError} If the request fails
 * 
 * @example
 * ```typescript
 * const results = await searchDocument(
 *   '123e4567-e89b-12d3-a456-426614174000',
 *   'BOARD_LOT_IN',
 *   1
 * );
 * console.log(results.total_results); // 23
 * ```
 * 
 * @see {@link SearchResults} for response structure
 */
async function searchDocument(
  documentId: string,
  query: string,
  page: number = 1
): Promise<SearchResults> {
  // Implementation
}

Documentation Checklist
Before Writing

 Understand the audience
 Identify key concepts to explain
 Gather examples and use cases
 Check existing documentation for consistency

While Writing

 Use clear, simple language
 Include code examples
 Add diagrams where helpful
 Highlight important notes/warnings
 Link to related documentation

After Writing

 Proofread for clarity
 Test all code examples
 Verify all links work
 Get peer review
 Update table of contents (if applicable)


Please follow documentation standards in .claude/conventions.md.