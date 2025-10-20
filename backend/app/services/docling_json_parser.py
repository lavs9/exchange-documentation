"""Parser for pre-processed Docling JSON output."""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DoclingParsingError(Exception):
    """Raised when Docling JSON parsing fails."""

    pass


class ParsedSection:
    """Represents a parsed section from Docling output."""

    def __init__(
        self,
        level: int,
        title: str,
        content: str,
        page_number: Optional[int] = None,
        order_index: int = 0,
    ) -> None:
        """Initialize parsed section."""
        self.level = level
        self.title = title
        self.content = content
        self.page_number = page_number
        self.order_index = order_index

    def __repr__(self) -> str:
        """String representation."""
        return f"<ParsedSection(level={self.level}, title='{self.title}', page={self.page_number})>"


class DoclingJSONParser:
    """
    Parser for Docling JSON output.

    Expects JSON structure from Docling with:
    - Document metadata
    - Main text content
    - Hierarchical sections/headings
    - Tables (optional)
    """

    def __init__(self) -> None:
        """Initialize parser."""
        logger.info("DoclingJSONParser initialized")

    def parse_json(self, json_path: Path) -> tuple[List[ParsedSection], int]:
        """
        Parse Docling JSON file into sections.

        Args:
            json_path: Path to Docling JSON output file

        Returns:
            Tuple of (sections, page_count)

        Raises:
            DoclingParsingError: If parsing fails
        """
        try:
            logger.info(f"Parsing Docling JSON: {json_path}")

            # Load JSON
            with open(json_path, "r", encoding="utf-8") as f:
                docling_data = json.load(f)

            # Extract page count
            page_count = self._extract_page_count(docling_data)

            # Parse sections from JSON structure
            sections = self._parse_sections_from_json(docling_data)

            # If no sections found, try parsing from markdown
            if not sections:
                logger.warning("No sections in JSON, attempting markdown fallback")
                sections = self._parse_from_markdown_fallback(docling_data)

            logger.info(f"Parsed {len(sections)} sections, {page_count} pages")

            return sections, page_count

        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_path}")
            raise DoclingParsingError(f"JSON file not found: {json_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise DoclingParsingError(f"Invalid JSON: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to parse Docling JSON: {e}", exc_info=True)
            raise DoclingParsingError(f"Parsing failed: {str(e)}") from e

    def parse_markdown(self, markdown_path: Path) -> tuple[List[ParsedSection], int]:
        """
        Parse Docling markdown file into sections.

        Args:
            markdown_path: Path to Docling markdown output file

        Returns:
            Tuple of (sections, page_count)

        Raises:
            DoclingParsingError: If parsing fails
        """
        try:
            logger.info(f"Parsing Docling markdown: {markdown_path}")

            # Load markdown
            with open(markdown_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            # Parse sections
            sections = self._parse_markdown_sections(markdown_content)

            # Estimate page count (rough: 500 words per page)
            word_count = len(markdown_content.split())
            page_count = max(1, word_count // 500)

            logger.info(f"Parsed {len(sections)} sections, ~{page_count} pages")

            return sections, page_count

        except FileNotFoundError:
            logger.error(f"Markdown file not found: {markdown_path}")
            raise DoclingParsingError(f"Markdown file not found: {markdown_path}")
        except Exception as e:
            logger.error(f"Failed to parse markdown: {e}", exc_info=True)
            raise DoclingParsingError(f"Parsing failed: {str(e)}") from e

    def _extract_page_count(self, docling_data: Dict[str, Any]) -> int:
        """Extract page count from Docling JSON."""
        # Try different possible locations for page count
        if "num_pages" in docling_data:
            return docling_data["num_pages"]

        if "page_count" in docling_data:
            return docling_data["page_count"]

        if "pages" in docling_data and isinstance(docling_data["pages"], list):
            return len(docling_data["pages"])

        if "main-text" in docling_data:
            # Count page markers in text
            text = str(docling_data["main-text"])
            page_markers = text.count("<!-- page-break -->")
            if page_markers > 0:
                return page_markers + 1

        # Default
        return 1

    def _parse_sections_from_json(self, docling_data: Dict[str, Any]) -> List[ParsedSection]:
        """
        Parse sections from Docling JSON structure.

        Docling JSON typically has:
        - "main-text": list of content elements
        - Each element has "type" and "text"
        - Types include: "paragraph", "section-header", "title", etc.
        """
        sections = []
        order_index = 0

        # Try to find main content
        main_content = None
        if "main-text" in docling_data:
            main_content = docling_data["main-text"]
        elif "body" in docling_data:
            main_content = docling_data["body"]
        elif "content" in docling_data:
            main_content = docling_data["content"]

        if not main_content:
            logger.warning("No main content found in JSON")
            return sections

        # If main_content is a string, parse as markdown
        if isinstance(main_content, str):
            return self._parse_markdown_sections(main_content)

        # If main_content is a list, parse structured elements
        if isinstance(main_content, list):
            current_section = None

            for element in main_content:
                if not isinstance(element, dict):
                    continue

                elem_type = element.get("type", "")
                text = element.get("text", "")
                page_num = element.get("page", None)

                # Check if this is a heading
                if "header" in elem_type.lower() or "title" in elem_type.lower():
                    # Save previous section
                    if current_section:
                        sections.append(ParsedSection(
                            level=current_section["level"],
                            title=current_section["title"],
                            content=current_section["content"].strip(),
                            page_number=current_section.get("page_number"),
                            order_index=order_index,
                        ))
                        order_index += 1

                    # Determine heading level (1-4)
                    level = 1
                    if "section-header" in elem_type:
                        level = 2
                    elif "subsection" in elem_type:
                        level = 3
                    elif "subsubsection" in elem_type:
                        level = 4

                    # Start new section
                    current_section = {
                        "level": level,
                        "title": text.strip(),
                        "content": "",
                        "page_number": page_num,
                    }

                elif current_section:
                    # Add content to current section
                    current_section["content"] += text + "\n\n"

            # Save last section
            if current_section:
                sections.append(ParsedSection(
                    level=current_section["level"],
                    title=current_section["title"],
                    content=current_section["content"].strip(),
                    page_number=current_section.get("page_number"),
                    order_index=order_index,
                ))

        return sections

    def _parse_from_markdown_fallback(self, docling_data: Dict[str, Any]) -> List[ParsedSection]:
        """
        Fallback: Try to find markdown content in JSON and parse it.
        """
        # Look for markdown content
        markdown = None
        if "markdown" in docling_data:
            markdown = docling_data["markdown"]
        elif "md" in docling_data:
            markdown = docling_data["md"]
        elif "main-text" in docling_data and isinstance(docling_data["main-text"], str):
            markdown = docling_data["main-text"]

        if markdown and isinstance(markdown, str):
            return self._parse_markdown_sections(markdown)

        return []

    def _parse_markdown_sections(self, markdown: str) -> List[ParsedSection]:
        """
        Parse markdown content into sections based on headers.

        Supports:
        - # Header (level 1)
        - ## Header (level 2)
        - ### Header (level 3)
        - #### Header (level 4)
        """
        sections = []
        lines = markdown.split("\n")

        current_section = None
        order_index = 0

        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)

            if heading_match:
                # Save previous section
                if current_section:
                    sections.append(ParsedSection(
                        level=current_section["level"],
                        title=current_section["title"],
                        content=current_section["content"].strip(),
                        page_number=current_section.get("page_number"),
                        order_index=order_index,
                    ))
                    order_index += 1

                # Start new section
                level = len(heading_match.group(1))  # Count # symbols
                level = min(level, 4)  # Cap at level 4
                title = heading_match.group(2).strip()

                current_section = {
                    "level": level,
                    "title": title,
                    "content": "",
                    "page_number": None,
                }

            elif current_section:
                # Add line to current section content
                current_section["content"] += line + "\n"

        # Save last section
        if current_section:
            sections.append(ParsedSection(
                level=current_section["level"],
                title=current_section["title"],
                content=current_section["content"].strip(),
                page_number=current_section.get("page_number"),
                order_index=order_index,
            ))

        return sections

    def extract_metadata(self, json_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from Docling JSON.

        Args:
            json_path: Path to Docling JSON file

        Returns:
            Dictionary of metadata
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                docling_data = json.load(f)

            metadata = {}

            # Extract common metadata fields
            if "title" in docling_data:
                metadata["title"] = docling_data["title"]

            if "author" in docling_data:
                metadata["author"] = docling_data["author"]

            if "date" in docling_data:
                metadata["date"] = docling_data["date"]

            if "version" in docling_data:
                metadata["version"] = docling_data["version"]

            metadata["parser"] = "docling-json"
            metadata["source"] = str(json_path)

            return metadata

        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            return {"source": str(json_path)}
