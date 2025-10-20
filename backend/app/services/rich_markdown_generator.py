"""Rich Markdown Generator for Docling JSON.

This module converts Docling JSON documents into chapter-based rich markdown with:
- Proper chapter detection using "Chapter X" pattern in level 1 headings
- Full markdown content for each chapter (for viewing)
- YAML frontmatter with metadata
- GFM tables with captions
- Page references throughout
- Obsidian-style callouts for important sections
- Internal cross-references between chapters

Architecture:
- ONE section per chapter in database (not per heading)
- Complete markdown stored for viewing
- Searchable text extracted separately for full-text search
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ChapterMarkdown:
    """Represents a single chapter's markdown content."""

    chapter_number: int
    title: str
    markdown_content: str  # Complete markdown for viewing
    searchable_text: str  # Plain text for search indexing
    page_range: Tuple[int, int]
    metadata: Dict[str, Any]
    anchor_id: str


class RichMarkdownGenerator:
    """Convert Docling JSON to rich, chapter-based markdown."""

    def __init__(self, docling_json: Dict[str, Any]):
        """Initialize with parsed Docling JSON."""
        self.json_data = docling_json
        self.texts = {t["self_ref"]: t for t in docling_json.get("texts", [])}
        self.tables = {t["self_ref"]: t for t in docling_json.get("tables", [])}
        self.pictures = {p["self_ref"]: p for p in docling_json.get("pictures", [])}
        self.groups = {g["self_ref"]: g for g in docling_json.get("groups", [])}

        # Build ordered list of body elements for sequential processing
        self.body_elements = self._resolve_body_children()

    def _resolve_body_children(self) -> List[Dict[str, Any]]:
        """Resolve all body children to actual elements."""
        body = self.json_data.get("body", {})
        children_refs = body.get("children", [])

        elements = []
        for child_ref in children_refs:
            ref = child_ref.get("$ref")
            element = self._resolve_ref(ref)
            if element:
                elements.append(element)

        return elements

    def _resolve_ref(self, ref: str) -> Optional[Dict[str, Any]]:
        """Resolve a $ref to the actual element."""
        if not ref:
            return None

        if ref in self.texts:
            return self.texts[ref]
        elif ref in self.tables:
            return self.tables[ref]
        elif ref in self.pictures:
            return self.pictures[ref]
        elif ref in self.groups:
            return self.groups[ref]
        return None

    def generate_chapters(self) -> List[ChapterMarkdown]:
        """
        Main entry point: Parse JSON and return list of chapters.

        Strategy:
        1. Find all "Chapter X" level 1 headings in body elements
        2. Group content between chapter boundaries
        3. Generate complete markdown for each chapter
        4. Extract searchable text separately
        5. Return list of ChapterMarkdown objects
        """
        logger.info("Starting chapter-based markdown generation from Docling JSON")

        # Step 1: Detect chapter boundaries
        chapter_boundaries = self._detect_chapter_boundaries()

        if not chapter_boundaries:
            logger.warning("No chapters found, creating single chapter from frontmatter")
            return [self._create_frontmatter_chapter()]

        logger.info(f"Detected {len(chapter_boundaries)} chapters")

        # Step 2: Generate markdown for each chapter
        chapter_markdowns = []
        for i, chapter_info in enumerate(chapter_boundaries):
            chapter_md = self._generate_chapter_markdown(chapter_info, i)
            chapter_markdowns.append(chapter_md)

        # Step 3: Add cross-references
        chapter_markdowns = self._add_cross_references(chapter_markdowns)

        return chapter_markdowns

    def _detect_chapter_boundaries(self) -> List[Dict[str, Any]]:
        """
        Detect chapter boundaries by finding 'Chapter X' level 1 headings.

        Returns list of:
        {
            'chapter_number': int,
            'title': str,
            'start_index': int,  # Index in body_elements
            'end_index': int,    # Index in body_elements
            'elements': List[Dict]  # All elements in this chapter
        }
        """
        boundaries = []
        chapter_pattern = re.compile(r'^Chapter\s+(\d+)', re.IGNORECASE)

        for i, element in enumerate(self.body_elements):
            # Check if this is a chapter header
            if element.get("label") == "section_header" and element.get("level") == 1:
                text = element.get("text", "")
                match = chapter_pattern.match(text)

                if match:
                    chapter_num = int(match.group(1))

                    # If we have a previous chapter, set its end_index
                    if boundaries:
                        boundaries[-1]['end_index'] = i

                    boundaries.append({
                        'chapter_number': chapter_num,
                        'title': text,
                        'start_index': i,
                        'end_index': len(self.body_elements),  # Will be updated
                        'header_element': element
                    })

        # Build element lists for each chapter
        for boundary in boundaries:
            start = boundary['start_index']
            end = boundary['end_index']
            boundary['elements'] = self.body_elements[start:end]

        return boundaries

    def _create_frontmatter_chapter(self) -> ChapterMarkdown:
        """Create a chapter from frontmatter (preface, TOC, etc.) when no chapters found."""
        # Get elements before first real chapter
        frontmatter_elements = []
        for element in self.body_elements:
            if element.get("label") == "section_header" and element.get("level") == 1:
                text = element.get("text", "")
                if re.match(r'^Chapter\s+\d+', text, re.IGNORECASE):
                    break
            frontmatter_elements.append(element)

        # Generate markdown
        md_parts = ["# Frontmatter\n"]
        for element in frontmatter_elements:
            md = self._element_to_markdown(element)
            if md:
                md_parts.append(md)

        markdown_content = "\n\n".join(md_parts)

        # Extract page range
        page_nums = [self._get_page_number(el) for el in frontmatter_elements]
        page_nums = [p for p in page_nums if p > 0]
        page_range = (min(page_nums) if page_nums else 1, max(page_nums) if page_nums else 1)

        return ChapterMarkdown(
            chapter_number=0,
            title="Frontmatter",
            markdown_content=markdown_content,
            searchable_text=self._extract_searchable_text(markdown_content),
            page_range=page_range,
            metadata={"type": "frontmatter"},
            anchor_id="frontmatter"
        )

    def _generate_chapter_markdown(
        self, chapter_info: Dict[str, Any], index: int
    ) -> ChapterMarkdown:
        """Generate complete rich markdown for a single chapter."""
        chapter_number = chapter_info['chapter_number']
        title = chapter_info['title']
        elements = chapter_info['elements']

        # Calculate page range
        page_nums = [self._get_page_number(el) for el in elements]
        page_nums = [p for p in page_nums if p > 0]
        start_page = min(page_nums) if page_nums else 1
        end_page = max(page_nums) if page_nums else start_page

        # Generate YAML frontmatter
        frontmatter = self._generate_frontmatter(title, chapter_number, start_page, end_page)

        # Generate chapter content
        md_parts = [frontmatter, f"# {title}\n"]

        # Filter out page footers and merge tables
        filtered_elements = self._filter_page_footers(elements[1:])
        merged_elements = self._merge_consecutive_tables(filtered_elements)

        # Convert elements to markdown
        for element in merged_elements:
            md = self._element_to_markdown(element)
            if md:
                md_parts.append(md)

        markdown_content = "\n\n".join(md_parts)

        # Add callouts
        markdown_content = self._add_callouts(markdown_content)

        # Extract searchable text
        searchable_text = self._extract_searchable_text(markdown_content)

        # Generate anchor ID
        anchor_id = self._generate_anchor_id(title)

        return ChapterMarkdown(
            chapter_number=chapter_number,
            title=title,
            markdown_content=markdown_content,
            searchable_text=searchable_text,
            page_range=(start_page, end_page),
            metadata={
                "element_count": len(elements),
                "original_title": title
            },
            anchor_id=anchor_id,
        )

    def _generate_frontmatter(
        self, title: str, chapter_number: int, start_page: int, end_page: int
    ) -> str:
        """Generate YAML frontmatter for chapter."""
        return f"""---
title: "{title}"
chapter_number: {chapter_number}
page_range: "{start_page}-{end_page}"
document: "{self.json_data.get('name', 'Unknown')}"
---"""

    def _generate_anchor_id(self, title: str) -> str:
        """Generate URL-safe anchor ID from title."""
        # Extract chapter number and create clean anchor
        match = re.match(r'^Chapter\s+(\d+)', title, re.IGNORECASE)
        if match:
            chapter_num = match.group(1)
            # Get the rest of the title after "Chapter X"
            rest = title[match.end():].strip()
            if rest:
                # Clean the rest of the title
                rest_clean = re.sub(r'[^a-z0-9\s-]', '', rest.lower())
                rest_clean = re.sub(r'\s+', '-', rest_clean)
                return f"chapter-{chapter_num}-{rest_clean}"
            else:
                return f"chapter-{chapter_num}"

        # Fallback for non-chapter titles
        anchor = title.lower()
        anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor

    def _get_page_number(self, element: Dict[str, Any]) -> int:
        """Extract page number from element."""
        prov = element.get("prov", [])
        if prov and len(prov) > 0:
            return prov[0].get("page_no", 0)
        return 0

    def _filter_page_footers(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out repetitive page footers and headers.

        Common patterns to remove:
        - "Non-Confidential"
        - Page numbers (standalone numbers)
        - Document title footers
        - Page break artifacts
        """
        filtered = []
        filtered_count = 0
        footer_patterns = [
            r'^Non-Confidential\s*$',
            r'^Confidential\s*$',
            r'^\d+\s*$',  # Standalone page numbers
            r'^Capital Market Trading System.*Protocol.*$',
            r'^Trading System.*Protocol.*$',
            r'^Page\s+\d+\s*$',
        ]

        for element in elements:
            label = element.get("label", "")
            text = element.get("text", "").strip()

            # Always skip page_header and page_footer elements from Docling
            if label in ["page_footer", "page_header"]:
                filtered_count += 1
                logger.debug(f"Filtered Docling footer/header: '{text}' (label: {label})")
                continue

            # Always keep non-text elements (tables, pictures, etc.)
            if label in ["table", "code", "list", "picture"]:
                filtered.append(element)
                continue

            # For text elements, check if they're footers
            if label in ["text", "section_header"]:
                # Skip if no text
                if not text:
                    continue

                # Check if this is a footer pattern
                is_footer = False
                for pattern in footer_patterns:
                    if re.match(pattern, text, re.IGNORECASE):
                        is_footer = True
                        filtered_count += 1
                        logger.debug(f"Filtered footer: '{text}' (matched: {pattern})")
                        break

                if not is_footer:
                    filtered.append(element)
            else:
                # Unknown label, keep it to be safe
                filtered.append(element)

        if filtered_count > 0:
            logger.info(f"Filtered {filtered_count} footer elements")
        return filtered

    def _merge_consecutive_tables(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge tables that continue across multiple pages.

        Tables are merged if:
        1. They appear consecutively (allowing text elements in between)
        2. They have the same column headers
        3. They appear on sequential or nearby pages
        """
        merged = []
        i = 0

        while i < len(elements):
            element = elements[i]

            # Check if current element is a table
            if element.get("label") == "table":
                current_table = element
                current_page = self._get_page_number(current_table)
                current_headers = self._get_table_headers(current_table)

                # Look ahead for continuation tables
                j = i + 1
                continuation_tables = []

                while j < len(elements):
                    next_elem = elements[j]
                    next_label = next_elem.get("label", "")

                    # Stop if we hit a section header (new section started)
                    if next_label == "section_header":
                        break

                    # Check if it's a table
                    if next_label == "table":
                        next_page = self._get_page_number(next_elem)
                        next_headers = self._get_table_headers(next_elem)

                        # Merge if headers match and pages are close
                        if (current_headers == next_headers and
                            0 <= next_page - current_page <= 3):
                            continuation_tables.append(next_elem)
                            j += 1
                        else:
                            # Different table, stop looking
                            break
                    elif next_label in ["text", "picture"]:
                        # Allow some text/images between table continuations
                        j += 1
                    else:
                        break

                # If we found continuation tables, merge them
                if continuation_tables:
                    merged_table = self._merge_table_elements(
                        current_table, continuation_tables
                    )
                    merged.append(merged_table)
                    i = j  # Skip all merged tables
                else:
                    merged.append(current_table)
                    i += 1
            else:
                merged.append(element)
                i += 1

        return merged

    def _get_table_headers(self, table_element: Dict[str, Any]) -> List[str]:
        """Extract header row from table element."""
        try:
            data = table_element.get("data", {})
            grid = data.get("grid", [])
            if grid and len(grid) > 0:
                headers = grid[0]
                return [cell.get("text", "").strip() for cell in headers]
        except Exception:
            pass
        return []

    def _merge_table_elements(
        self,
        first_table: Dict[str, Any],
        continuation_tables: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge multiple table elements into one."""
        # Create a copy of the first table
        merged = dict(first_table)

        try:
            # Get the grid from first table
            merged_data = dict(first_table.get("data", {}))
            merged_grid = list(merged_data.get("grid", []))

            # Append rows from continuation tables (skip their header rows)
            for cont_table in continuation_tables:
                cont_data = cont_table.get("data", {})
                cont_grid = cont_data.get("grid", [])

                # Skip header row (first row) and append the rest
                if len(cont_grid) > 1:
                    merged_grid.extend(cont_grid[1:])

            # Update the merged table data
            merged_data["grid"] = merged_grid
            merged["data"] = merged_data

            # Update page range in prov to show it spans multiple pages
            first_page = self._get_page_number(first_table)
            last_page = self._get_page_number(continuation_tables[-1])

            # Keep first table's prov but note the page range in metadata
            merged["_merged_pages"] = f"{first_page}-{last_page}"

        except Exception as e:
            logger.warning(f"Failed to merge tables: {e}")
            return first_table

        return merged

    def _element_to_markdown(self, element: Dict[str, Any]) -> Optional[str]:
        """Convert a Docling element to markdown."""
        label = element.get("label", "")

        if label == "text":
            return self._text_to_markdown(element)
        elif label == "section_header":
            return self._header_to_markdown(element)
        elif label == "table":
            return self._table_to_markdown(element)
        elif label == "picture":
            return self._picture_to_markdown(element)
        elif label == "code":
            return self._code_to_markdown(element)
        elif label == "list":
            return self._group_to_markdown(element)
        else:
            # Default: treat as text
            text = element.get("text", "")
            return text if text else None

    def _text_to_markdown(self, element: Dict[str, Any]) -> str:
        """Convert text element to markdown."""
        text = element.get("text", "").strip()
        if not text:
            return ""

        # No page references - they render as code blocks in TipTap
        return text

    def _header_to_markdown(self, element: Dict[str, Any]) -> str:
        """Convert section header to markdown."""
        text = element.get("text", "").strip()
        if not text:
            return ""

        level = element.get("level", 2)

        # In chapter-based architecture, level 1 headers become h2 (since chapter title is h1)
        # level 2 becomes h3, etc.
        md_level = "#" * min(level + 1, 6)

        # No page references - they render as code blocks in TipTap
        return f"{md_level} {text}"

    def _table_to_markdown(self, element: Dict[str, Any]) -> str:
        """Convert table to GFM markdown with caption."""
        data = element.get("data", {})
        grid = data.get("grid", [])
        page_no = self._get_page_number(element)

        if not grid or len(grid) < 2:  # Need at least header + 1 row
            return ""

        md_lines = []

        # No page references - they render as code blocks in TipTap
        # Tables are self-explanatory without page numbers

        try:
            # Handle colspan in table cells - Docling repeats cells with col_span
            # We need to deduplicate them
            def deduplicate_row(row):
                """Remove duplicate cells caused by colspan."""
                seen = {}
                unique_cells = []

                for cell in row:
                    text = cell.get("text", "").strip()
                    col_span = cell.get("col_span", 1)
                    start_col = cell.get("start_col_offset_idx", len(unique_cells))

                    # Create a unique key for this cell position
                    cell_key = f"{start_col}_{text}"

                    if cell_key not in seen:
                        seen[cell_key] = True
                        unique_cells.append(cell)

                return unique_cells

            # Extract and deduplicate headers (first row)
            headers = deduplicate_row(grid[0])
            header_texts = [self._clean_cell_text(cell.get("text", "")) for cell in headers]

            # If first row is truly header-like, use it as headers
            # Otherwise, treat the whole table as data
            num_cols = len(header_texts)

            # Build header row
            md_lines.append("| " + " | ".join(header_texts) + " |")

            # Build separator row
            md_lines.append("| " + " | ".join(["---"] * num_cols) + " |")

            # Build data rows
            for row in grid[1:]:
                deduped_row = deduplicate_row(row)
                row_texts = [self._clean_cell_text(cell.get("text", "")) for cell in deduped_row]

                # Pad row if needed to match header column count
                while len(row_texts) < num_cols:
                    row_texts.append("")
                md_lines.append("| " + " | ".join(row_texts[:num_cols]) + " |")

            return "\n".join(md_lines)
        except Exception as e:
            logger.warning(f"Failed to convert table: {e}")
            return "*[Table content could not be rendered]*"

    def _clean_cell_text(self, text: str) -> str:
        """Clean table cell text for markdown."""
        if not text:
            return ""
        # Remove newlines and extra whitespace
        text = " ".join(text.split())
        # Escape pipe characters
        text = text.replace("|", "\\|")
        return text

    def _picture_to_markdown(self, element: Dict[str, Any]) -> str:
        """Convert picture to markdown placeholder."""
        # Skip images entirely as per user request
        # Images are typically page decorations or logos
        return None

    def _code_to_markdown(self, element: Dict[str, Any]) -> str:
        """Convert code block to markdown with language hint."""
        text = element.get("text", "")

        # Try to detect language
        lang = self._detect_code_language(text)

        # No page references - they render as code blocks in TipTap
        return f"```{lang}\n{text}\n```"

    def _detect_code_language(self, code: str) -> str:
        """Simple language detection for code blocks."""
        code_lower = code.lower()
        if "import " in code_lower or "def " in code_lower:
            return "python"
        elif "{" in code and "}" in code and ";" in code:
            return "c"
        elif "function" in code_lower or "const " in code_lower:
            return "javascript"
        return ""

    def _group_to_markdown(self, element: Dict[str, Any]) -> str:
        """Convert group (list) to markdown."""
        children = element.get("children", [])
        if not children:
            return ""

        md_parts = []
        for child_ref in children:
            ref = child_ref.get("$ref")
            child_element = self._resolve_ref(ref)
            if child_element:
                text = child_element.get("text", "").strip()
                if text:
                    md_parts.append(f"- {text}")

        return "\n".join(md_parts) if md_parts else ""

    def _add_callouts(self, markdown: str) -> str:
        """
        Add Obsidian-style callouts for important patterns.

        Patterns:
        - "Note:" or "NOTE:" -> [!note]
        - "Important:" or "IMPORTANT:" -> [!important]
        - "Warning:" or "WARNING:" -> [!warning]
        - "Tip:" or "TIP:" -> [!tip]
        """
        # Note patterns
        markdown = re.sub(
            r'^(Note:|NOTE:)\s*(.+)$',
            r'> [!note]\n> \2',
            markdown,
            flags=re.MULTILINE,
        )

        # Important patterns
        markdown = re.sub(
            r'^(Important:|IMPORTANT:)\s*(.+)$',
            r'> [!important]\n> \2',
            markdown,
            flags=re.MULTILINE,
        )

        # Warning patterns
        markdown = re.sub(
            r'^(Warning:|WARNING:)\s*(.+)$',
            r'> [!warning]\n> \2',
            markdown,
            flags=re.MULTILINE,
        )

        # Tip patterns
        markdown = re.sub(
            r'^(Tip:|TIP:)\s*(.+)$',
            r'> [!tip]\n> \2',
            markdown,
            flags=re.MULTILINE,
        )

        return markdown

    def _extract_searchable_text(self, markdown: str) -> str:
        """
        Extract plain searchable text from markdown.

        Removes:
        - YAML frontmatter
        - Markdown formatting (*, _, #, etc.)
        - Page references
        - Image tags
        - Code blocks (keeps content but removes fences)
        """
        text = markdown

        # Remove YAML frontmatter
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)

        # Remove page references
        text = re.sub(r'`\[p\.\d+\]`', '', text)

        # Remove image tags
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

        # Remove code block fences (keep content)
        text = re.sub(r'```[a-z]*\n(.*?)\n```', r'\1', text, flags=re.DOTALL)

        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)

        # Remove headings markers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

        # Remove bold/italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove callouts
        text = re.sub(r'> \[!.*?\]\n> ', '', text)

        # Clean up whitespace
        text = re.sub(r'\n\n+', '\n\n', text)

        return text.strip()

    def _add_cross_references(
        self, chapters: List[ChapterMarkdown]
    ) -> List[ChapterMarkdown]:
        """
        Add internal cross-references between chapters.

        Pattern: "Chapter X" -> [Chapter X](#chapter-x-title) (p.XX)
        """
        # Build chapter map
        chapter_map = {}
        for ch in chapters:
            if ch.chapter_number > 0:  # Skip frontmatter
                chapter_map[ch.chapter_number] = (ch.anchor_id, ch.page_range[0])

        # Update each chapter's content
        updated_chapters = []
        for chapter in chapters:
            content = chapter.markdown_content

            # Find "Chapter X" references
            for ch_num, (anchor, page) in chapter_map.items():
                if ch_num != chapter.chapter_number:  # Don't link to self
                    # Match "Chapter X" not followed by markdown link
                    pattern = rf'\bChapter\s+{ch_num}\b(?!\]\()'
                    replacement = f"[Chapter {ch_num}](#{anchor})"
                    content = re.sub(pattern, replacement, content)

            # Create updated chapter
            updated_chapter = ChapterMarkdown(
                chapter_number=chapter.chapter_number,
                title=chapter.title,
                markdown_content=content,
                searchable_text=chapter.searchable_text,
                page_range=chapter.page_range,
                metadata=chapter.metadata,
                anchor_id=chapter.anchor_id,
            )
            updated_chapters.append(updated_chapter)

        return updated_chapters


def generate_rich_markdown_from_json(
    docling_json: Dict[str, Any]
) -> List[ChapterMarkdown]:
    """
    Main entry point: Generate rich markdown chapters from Docling JSON.

    Args:
        docling_json: Parsed Docling JSON document

    Returns:
        List of ChapterMarkdown objects with complete markdown and searchable text
    """
    generator = RichMarkdownGenerator(docling_json)
    chapters = generator.generate_chapters()

    logger.info(f"Generated {len(chapters)} chapters with rich markdown")
    for ch in chapters:
        logger.info(
            f"  Chapter {ch.chapter_number}: '{ch.title}' "
            f"(pages {ch.page_range[0]}-{ch.page_range[1]}, "
            f"{len(ch.markdown_content)} chars markdown, "
            f"{len(ch.searchable_text)} chars searchable)"
        )

    return chapters
