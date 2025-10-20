@.claude/architecture.md (see updated Document Processing Flow section)
@.claude/conventions.md

I need to implement rich markdown generation from Docling JSON with chapter-based document organization.

**CURRENT STATE**:
- ✅ Frontend upload UI exists
- ✅ TOC display component exists
- ✅ Basic document processor exists
- ✅ Database models exist (documents, sections tables)
- ✅ Markdown renderer component exists
- ✅ TOC generator exists (needs update to work with chapters)

**WHAT WE'RE BUILDING**:
1. Accept Docling JSON files (primary) and Markdown files (secondary)
2. Parse JSON and generate rich markdown organized by chapters
3. Create ONE section per chapter in database (efficient loading)
4. Update existing TOC generator to work with chapter-based structure
5. Support internal cross-references between chapters

**CHAPTER-BASED ARCHITECTURE**:
NSE protocol has ~300 pages across 12+ chapters. Instead of one massive document:
- Each chapter = one database section
- Faster loading (load chapter on demand)
- Better search (chapter-scoped results)
- Easier navigation

**DOCLING MCP ACCESS**:
I have Docling MCP enabled. Please reference Docling documentation for:
- DoclingDocument structure
- DocItem types (TextItem, TableItem, HeadingItem, RefItem)
- Table data structure
- Cross-reference handling

---

## TASK 1: Create RichMarkdownGenerator

**File**: `backend/app/services/rich_markdown_generator.py`

**Purpose**: 
Convert Docling JSON → Rich Markdown organized by chapters

**Chapter Detection Strategy**:
1. **Primary**: Use Docling's TOC structure if available
2. **Fallback**: Detect H1 headings as chapter boundaries
3. Extract page ranges for each chapter

**Rich Markdown Features**:
- ✅ YAML frontmatter per chapter (title, chapter_number, page_range)
- ✅ GitHub Flavored Markdown tables with captions
- ✅ Obsidian-style callouts: `> [!note]`, `> [!tip]`, `> [!warning]`, `> [!important]`
- ✅ Page references: `` `[p.56]` ``
- ✅ Internal cross-references: `[Order Entry](#chapter-4-order-entry) (p.46)`
- ✅ Code blocks with language hints: `` ```python ``
- ✅ Inline formatting preservation (bold, italic, code)

**Implementation**:
```python
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from docling_core.types.doc import DoclingDocument, DocItem, TableItem, TextItem, HeadingItem, RefItem

@dataclass
class ChapterMarkdown:
    """Represents a single chapter's markdown content."""
    chapter_number: int
    title: str
    markdown_content: str
    page_range: Tuple[int, int]  # (start_page, end_page)
    metadata: Dict
    anchor_id: str  # For internal linking

class RichMarkdownGenerator:
    """
    Convert Docling JSON to rich, chapter-based markdown.
    Optimized for readability and annotations.
    """
    
    def generate_chapters(self, docling_json: Dict) -> List[ChapterMarkdown]:
        """
        Main entry point: Parse JSON and return list of chapters.
        
        Strategy:
        1. Parse JSON into DoclingDocument
        2. Try to use Docling TOC for chapter boundaries
        3. Fallback to H1 heading detection
        4. Generate markdown for each chapter
        5. Return list of ChapterMarkdown objects
        """
        
    def _parse_docling_document(self, json_data: Dict) -> DoclingDocument:
        """Parse JSON into Docling document object using docling-core"""
        
    def _detect_chapters(self, doc: DoclingDocument) -> List['ChapterInfo']:
        """
        Detect chapter boundaries using hybrid approach:
        1. Check if doc has TOC structure
        2. If yes: extract chapters from TOC
        3. If no: scan for H1 headings
        4. Return list with chapter title, page range, item indices
        """
        
    def _generate_chapter_markdown(
        self, 
        chapter_info: 'ChapterInfo',
        doc_items: List[DocItem],
        all_chapters: List['ChapterInfo']  # For cross-references
    ) -> str:
        """
        Generate rich markdown for a single chapter.
        
        Process:
        1. Add YAML frontmatter
        2. Iterate through chapter's doc items
        3. Format each item type appropriately
        4. Handle cross-references to other chapters
        5. Return complete markdown string
        """
        
    def _generate_frontmatter(self, chapter_info: 'ChapterInfo') -> str:
        """
        Create YAML frontmatter.
        
        Example:
        ---
        title: Order and Trade Management
        chapter: 4
        pages: 46-72
        sections: 15
        ---
        """
        
    def _format_table(self, table_item: TableItem, page_num: int) -> str:
        """
        Format table as GFM with caption and metadata.
        
        Example:
        > **Table 19:** ORDER_ENTRY_REQUEST
        > *Page 50*
        
        | Field | Type | Size | Offset |
        | --- | --- | ---: | ---: |
        | TransactionCode | SHORT | 2 | 0 |
        """
        
    def _format_heading(
        self, 
        heading_item: HeadingItem,
        level_offset: int = -1  # Convert h1 to h2 within chapter
    ) -> str:
        """
        Format heading with anchor and page reference.
        
        Example:
        ## Section 4.1: Order Entry `[p.46]` {#chapter-4-order-entry}
        """
        
    def _format_code_block(self, code_item: CodeItem, page_num: int) -> str:
        """
        Format code block with language hint.
        
        Example:
```python  # Page 56
        @dataclass
        class OrderFlags:
            mf: bool = False
    """
    
def _format_reference(
    self, 
    ref_item: RefItem,
    all_chapters: List['ChapterInfo']
) -> str:
    """
    Format internal reference as markdown link.
    
    Priority:
    1. Link to specific sub-section if available: [Order Entry](#chapter-4-order-entry)
    2. Fallback to chapter: [Chapter 4](#chapter-4)
    3. Add page number: (p.46)
    
    Example:
    [Order Entry](#chapter-4-order-entry) *(p.46)*
    """
    
def _process_inline_formatting(
    self, 
    text: str, 
    formatting_spans: Dict
) -> str:
    """
    Apply inline formatting: **bold**, *italic*, `code`
    Process in order: bold -> italic -> code to avoid conflicts
    """
    
def _add_callout(self, text: str, callout_type: str = 'note') -> str:
    """
    Create Obsidian-style callout.
    
    Types: note, tip, warning, important, error
    
    Example:
    > [!important] ❗
    > All flags default to False unless explicitly set.
    """
    
def _detect_callout_worthy_content(self, text: str) -> Optional[str]:
    """
    Heuristic to detect content that should be a callout.
    Keywords: "important", "note", "warning", "caution", etc.
    """
    
def _slugify(self, text: str) -> str:
    """
    Convert text to anchor ID.
    Example: "Chapter 4: Order Entry" -> "chapter-4-order-entry"
    """
    
def _detect_alignment(self, table_rows: List[List[str]]) -> List[str]:
    """
    Detect column alignment for GFM tables.
    Numeric columns -> right align
    Text columns -> left align
    """
@dataclass
class ChapterInfo:
"""Internal structure for chapter metadata."""
chapter_number: int
title: str
page_start: int
page_end: int
start_item_idx: int
end_item_idx: int
anchor_id: str

**Use Docling MCP** to understand:
- How to check if `DoclingDocument` has TOC
- Structure of TOC items
- How to iterate through `DocItem` list
- Table structure in `TableItem.data`
- Reference format in `RefItem`

---

## TASK 2: Update DocumentProcessor

**File**: `backend/app/services/document_processor.py`

**Changes**:
```python
from app.services.rich_markdown_generator import RichMarkdownGenerator, ChapterMarkdown

class DocumentProcessor:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._markdown_generator = RichMarkdownGenerator()
        self._toc_generator = TOCGenerator()  # Keep existing
        
    async def process_document(
        self, 
        file: UploadFile,
        title: str,
        version: str,
        file_type: str  # "json" or "markdown"
    ) -> Document:
        """
        Process uploaded file (JSON or Markdown).
        
        Flow:
        1. Save file to disk
        2. Create document record (status='processing')
        3. If JSON: generate chapters using RichMarkdownGenerator
        4. If Markdown: treat entire content as single chapter
        5. Save chapters as sections in database
        6. Generate TOC using updated TOCGenerator
        7. Update status to 'completed'
        """
        try:
            # Save file
            file_path = await self._save_file(file)
            
            # Create document record
            document = await self._create_document_record(
                title=title,
                version=version,
                file_path=file_path,
                file_type=file_type
            )
            
            # Generate chapters
            if file_type == "json":
                chapters = await self._process_json(file_path)
            else:  # markdown
                chapters = await self._process_markdown(file_path, title)
            
            # Save chapters as sections
            await self._save_chapters_as_sections(document.id, chapters)
            
            # Generate TOC from all chapter sections
            toc = await self._generate_toc(document.id)
            
            # Update document status
            await self._update_document_status(document.id, 'completed')
            
            return document
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}", exc_info=True)
            await self._update_document_status(document.id, 'failed')
            raise DocumentProcessingError(str(e))
    
    async def _process_json(self, file_path: str) -> List[ChapterMarkdown]:
        """
        Process Docling JSON file.
        
        Steps:
        1. Read JSON file
        2. Call RichMarkdownGenerator.generate_chapters()
        3. Return list of chapters
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        chapters = self._markdown_generator.generate_chapters(json_data)
        return chapters
    
    async def _process_markdown(
        self, 
        file_path: str,
        title: str
    ) -> List[ChapterMarkdown]:
        """
        Process plain markdown file.
        
        Strategy:
        - Treat entire markdown as single chapter
        - Extract page numbers if present in content
        - Create ChapterMarkdown object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create single chapter
        chapter = ChapterMarkdown(
            chapter_number=1,
            title=title,
            markdown_content=content,
            page_range=(1, 1),
            metadata={},
            anchor_id=self._slugify(title)
        )
        
        return [chapter]
    
    async def _save_chapters_as_sections(
        self,
        document_id: UUID,
        chapters: List[ChapterMarkdown]
    ) -> None:
        """
        Save each chapter as a section in database.
        
        Section schema:
        - level: 1 (chapter level)
        - title: Chapter title
        - content: Full chapter markdown
        - page_number: Chapter start page
        - order_index: Chapter number
        - parent_id: None (chapters are top-level)
        """
        for chapter in chapters:
            section = Section(
                id=uuid4(),
                document_id=document_id,
                level=1,
                title=chapter.title,
                content=chapter.markdown_content,
                page_number=chapter.page_range[0],
                parent_id=None,
                order_index=chapter.chapter_number
            )
            self._db.add(section)
        
        await self._db.commit()
    
    async def _generate_toc(self, document_id: UUID) -> TableOfContents:
        """
        Generate TOC from all chapter sections.
        
        Strategy:
        1. Load all sections for document (ordered by order_index)
        2. For each chapter section, parse its markdown to extract nested headings
        3. Build complete TOC tree with chapters and sub-sections
        4. Use updated TOCGenerator
        """
        # Load all chapter sections
        sections = await self._db.execute(
            select(Section)
            .where(Section.document_id == document_id)
            .order_by(Section.order_index)
        )
        sections = sections.scalars().all()
        
        # Generate TOC
        toc = self._toc_generator.generate_from_chapters(sections)
        return toc

TASK 3: Update TOCGenerator
File: backend/app/services/toc_generator.py
Update to work with chapter-based structure:
pythonfrom typing import List
from app.models.section import Section

class TOCGenerator:
    """Generate table of contents from chapter sections."""
    
    def generate_from_chapters(self, chapter_sections: List[Section]) -> TableOfContents:
        """
        Generate complete TOC from list of chapter sections.
        
        Strategy:
        1. Each section is a chapter (level 1)
        2. Parse markdown in each chapter to extract nested headings (h2, h3, h4)
        3. Build hierarchical TOCEntry tree
        4. Return TableOfContents object
        """
        toc_entries = []
        
        for chapter_section in chapter_sections:
            # Create chapter TOC entry
            chapter_entry = TOCEntry(
                section_id=chapter_section.id,
                title=chapter_section.title,
                level=1,
                page_number=chapter_section.page_number,
                anchor_id=self._extract_anchor_from_markdown(chapter_section.content),
                children=[]
            )
            
            # Parse chapter markdown to extract nested headings
            nested_headings = self._extract_nested_headings(chapter_section.content)
            
            # Build child entries
            chapter_entry.children = self._build_nested_entries(nested_headings)
            
            toc_entries.append(chapter_entry)
        
        return TableOfContents(entries=toc_entries)
    
    def _extract_nested_headings(self, markdown: str) -> List['HeadingInfo']:
        """
        Extract h2, h3, h4 headings from markdown.
        
        Parse patterns like:
        ## Section 4.1 `[p.46]` {#chapter-4-order-entry}
        ### Subsection 4.1.1 `[p.47]`
        """
        import re
        
        headings = []
        # Regex to match: ## Title `[p.N]` {#anchor}
        pattern = r'^(#{2,4})\s+(.+?)(?:\s+`\[p\.(\d+)\]`)?(?:\s+\{#([^}]+)\})?$'
        
        for line in markdown.split('\n'):
            match = re.match(pattern, line)
            if match:
                level = len(match.group(1))  # Count #'s
                title = match.group(2).strip()
                page = int(match.group(3)) if match.group(3) else None
                anchor = match.group(4) if match.group(4) else self._slugify(title)
                
                headings.append(HeadingInfo(
                    level=level,
                    title=title,
                    page_number=page,
                    anchor_id=anchor
                ))
        
        return headings
    
    def _build_nested_entries(
        self, 
        headings: List['HeadingInfo']
    ) -> List[TOCEntry]:
        """
        Build hierarchical structure from flat heading list.
        
        Algorithm:
        - Stack-based approach to track current parent at each level
        - h2 -> level 2, h3 -> level 3, h4 -> level 4
        """
        # Implementation similar to existing TOCGenerator
        # but working with HeadingInfo objects
        pass
    
    def _extract_anchor_from_markdown(self, markdown: str) -> str:
        """Extract anchor ID from first heading in markdown."""
        import re
        match = re.search(r'\{#([^}]+)\}', markdown)
        return match.group(1) if match else ''
    
    def _slugify(self, text: str) -> str:
        """Convert text to anchor ID."""
        return text.lower().replace(' ', '-').replace('/', '-')

@dataclass
class HeadingInfo:
    """Internal structure for heading metadata."""
    level: int
    title: str
    page_number: Optional[int]
    anchor_id: str

@dataclass
class TOCEntry:
    """Table of contents entry."""
    section_id: UUID
    title: str
    level: int
    page_number: Optional[int]
    anchor_id: str
    children: List['TOCEntry']

@dataclass
class TableOfContents:
    """Complete table of contents."""
    entries: List[TOCEntry]

TASK 4: Update API Endpoint
File: backend/app/api/documents.py
Update upload endpoint to accept file_type:
python@router.post("/upload")
async def upload_document(
    file: UploadFile = File(..., description="Docling JSON or Markdown file"),
    title: str = Form(..., description="Document title"),
    version: str = Form(..., description="Document version"),
    file_type: str = Form(..., regex="^(json|markdown)$", description="File type: json or markdown"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload Docling JSON or Markdown file for processing.
    
    Supported formats:
    - json: Docling JSON output (primary, generates chapter-based sections)
    - markdown: Plain markdown (fallback, treated as single chapter)
    """
    
    # Validate file extension matches file_type
    file_ext = file.filename.split('.')[-1].lower()
    if (file_type == "json" and file_ext != "json") or \
       (file_type == "markdown" and file_ext not in ["md", "markdown"]):
        raise HTTPException(
            status_code=400,
            detail=f"File extension .{file_ext} doesn't match file_type {file_type}"
        )
    
    try:
        document = await document_processor.process_document(
            file=file,
            title=title,
            version=version,
            file_type=file_type
        )
        
        return DocumentResponse(
            id=document.id,
            title=document.title,
            version=document.version,
            status=document.processing_status,
            upload_date=document.upload_date,
            page_count=document.page_count
        )
        
    except DocumentProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))

TASK 5: Update Frontend Upload UI
File: frontend/src/components/DocumentUpload.tsx (or wherever upload UI is)
Minor updates:
typescriptconst [fileType, setFileType] = useState<'json' | 'markdown'>('json');

// In JSX:
<div>
  <label>File Type:</label>
  <select value={fileType} onChange={(e) => setFileType(e.target.value)}>
    <option value="json">Docling JSON (Recommended)</option>
    <option value="markdown">Plain Markdown</option>
  </select>
</div>

<input
  type="file"
  accept={fileType === 'json' ? 'application/json,.json' : '.md,.markdown,text/markdown'}
  onChange={handleFileChange}
/>

<p className="text-sm text-gray-500">
  {fileType === 'json' 
    ? 'Upload Docling JSON file (pre-processed from PDF with chapter structure)'
    : 'Upload plain markdown file (will be treated as single chapter)'
  }
</p>

// In upload function:
const formData = new FormData();
formData.append('file', file);
formData.append('title', title);
formData.append('version', version);
formData.append('file_type', fileType);  // NEW

TASK 6: Create Tests
File: backend/tests/test_rich_markdown_generator.py
pythonimport pytest
import json
from app.services.rich_markdown_generator import RichMarkdownGenerator

class TestRichMarkdownGenerator:
    
    @pytest.fixture
    def generator(self):
        return RichMarkdownGenerator()
    
    @pytest.fixture
    def sample_docling_json(self):
        """
        Load sample Docling JSON with 2-3 chapters.
        Create this fixture with minimal structure for testing.
        """
        return {
            "pages": [...],
            "items": [...]
        }
    
    def test_generate_chapters(self, generator, sample_docling_json):
        """Test basic chapter generation from JSON."""
        chapters = generator.generate_chapters(sample_docling_json)
        
        assert len(chapters) > 0
        assert all(isinstance(c, ChapterMarkdown) for c in chapters)
        assert all(c.markdown_content for c in chapters)
    
    def test_chapter_detection_from_toc(self, generator):
        """Test chapter detection using Docling TOC."""
        # Mock JSON with TOC structure
        pass
    
    def test_chapter_detection_from_h1(self, generator):
        """Test fallback chapter detection using H1 headings."""
        # Mock JSON without TOC but with H1 headings
        pass
    
    def test_table_formatting(self, generator):
        """Verify tables are formatted as GFM with captions."""
        # Test TableItem -> Markdown conversion
        pass
    
    def test_internal_references(self, generator):
        """Verify cross-chapter references are formatted correctly."""
        # Test RefItem -> Markdown link conversion
        pass
    
    def test_callout_generation(self, generator):
        """Verify callouts are added for important content."""
        result = generator._add_callout("Important note", "warning")
        assert "> [!warning]" in result
    
    def test_yaml_frontmatter(self, generator):
        """Verify YAML frontmatter is generated."""
        # Test _generate_frontmatter method
        pass
File: backend/tests/test_document_processor.py
pythonimport pytest
from app.services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    
    async def test_process_json_file(self, db_session, sample_json_file):
        """Test processing of Docling JSON file."""
        processor = DocumentProcessor(db_session)
        
        document = await processor.process_document(
            file=sample_json_file,
            title="Test Document",
            version="1.0",
            file_type="json"
        )
        
        assert document.processing_status == "completed"
        assert document.page_count > 0
    
    async def test_process_markdown_file(self, db_session, sample_markdown_file):
        """Test processing of plain markdown file."""
        processor = DocumentProcessor(db_session)
        
        document = await processor.process_document(
            file=sample_markdown_file,
            title="Test Document",
            version="1.0",
            file_type="markdown"
        )
        
        assert document.processing_status == "completed"
    
    async def test_chapters_saved_as_sections(self, db_session, sample_json_file):
        """Verify chapters are saved as sections in database."""
        # After processing, query sections and verify structure
        pass

DELIVERABLES CHECKLIST:

 RichMarkdownGenerator with chapter detection (TOC + H1 fallback)
 Updated DocumentProcessor (handles JSON and Markdown)
 Updated TOCGenerator (works with chapter sections)
 Updated API endpoint (file_type parameter)
 Updated frontend upload UI (file type selector)
 Tests for markdown generation
 Tests for document processing


TESTING PLAN:

Unit Tests: Run pytest on generator and processor
Integration Test:

Upload sample Docling JSON /Users/mayanklavania/projects/exchange-documentation-claude/sample-exchange-docs/output.json
Verify chapters are created
Check TOC structure


Real Data Test:

Get Docling JSON for NSE NNF Protocol
Upload and verify ~12 chapters created
Test search across chapters
Verify internal links work




NEXT STEPS AFTER IMPLEMENTATION:

Test with real NSE protocol Docling JSON
Fine-tune markdown formatting based on output
Add more callout detection heuristics
Optimize cross-reference resolution
Add chapter navigation in UI

Ready to start? Let's begin with RichMarkdownGenerator!