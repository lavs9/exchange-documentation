"""Table of Contents generation service."""
import logging
import re
from typing import Dict, List, Optional
from uuid import UUID

from app.models.section import Section
from app.schemas.document import TOCEntry

logger = logging.getLogger(__name__)


class TOCGenerationError(Exception):
    """Raised when TOC generation fails."""

    pass


class TOCGenerator:
    """Generates hierarchical table of contents from flat section list."""

    def __init__(self) -> None:
        """Initialize TOC generator."""
        self._section_map: Dict[UUID, Section] = {}

    def generate_toc(self, sections: List[Section]) -> List[TOCEntry]:
        """
        Build hierarchical TOC from flat section list.

        Algorithm:
        1. Sort sections by order_index
        2. Maintain a stack of current path (parent sections)
        3. For each section:
           - Pop stack until we find appropriate parent based on level
           - Link section to parent
           - Push section onto stack if it could be a parent

        Args:
            sections: Flat list of sections from database

        Returns:
            List of top-level TOCEntry objects with nested children

        Raises:
            TOCGenerationError: If TOC building fails
        """
        try:
            if not sections:
                logger.warning("No sections provided for TOC generation")
                return []

            # Build section map for quick lookup
            self._section_map = {s.id: s for s in sections}

            # Sort by order_index to ensure correct sequence
            sorted_sections = sorted(sections, key=lambda s: s.order_index)

            logger.info(f"Building TOC from {len(sorted_sections)} sections")

            # Build the tree structure
            root_entries = self._build_tree(sorted_sections)

            logger.info(f"Generated TOC with {len(root_entries)} root entries")

            return root_entries

        except Exception as e:
            logger.error(f"TOC generation failed: {e}", exc_info=True)
            raise TOCGenerationError(f"Failed to generate TOC: {str(e)}") from e

    def _build_tree(self, sections: List[Section]) -> List[TOCEntry]:
        """
        Build tree structure using stack-based algorithm.

        Args:
            sections: Sorted list of sections

        Returns:
            List of root TOCEntry objects
        """
        root_entries: List[TOCEntry] = []
        stack: List[TOCEntry] = []  # Stack of potential parent entries

        for section in sections:
            # Create TOC entry for this section
            entry = TOCEntry(
                id=section.id,
                title=section.title,
                level=section.level,
                page_number=section.page_number,
                children=[],
            )

            # Find appropriate parent based on level
            parent_entry = self._find_parent(stack, entry.level)

            if parent_entry:
                # Add as child to parent
                parent_entry.children.append(entry)
            else:
                # This is a root entry
                root_entries.append(entry)

            # Push current entry onto stack (it could be a parent for next entries)
            # But first, pop any entries at same or deeper level
            while stack and stack[-1].level >= entry.level:
                stack.pop()

            stack.append(entry)

        return root_entries

    def _find_parent(
        self, stack: List[TOCEntry], current_level: int
    ) -> Optional[TOCEntry]:
        """
        Find appropriate parent entry from stack based on level.

        Args:
            stack: Stack of potential parent entries
            current_level: Level of current section

        Returns:
            Parent TOCEntry or None if this should be a root entry
        """
        # Pop entries from stack until we find one with lower level
        # (which would be the parent)
        while stack:
            if stack[-1].level < current_level:
                # Found parent
                return stack[-1]
            # Current stack top is same level or deeper - not a parent
            if stack[-1].level >= current_level:
                break

        return None

    def generate_flat_toc(self, sections: List[Section]) -> List[TOCEntry]:
        """
        Generate flat (non-hierarchical) TOC for simple use cases.

        Args:
            sections: List of sections

        Returns:
            Flat list of TOCEntry objects without nesting
        """
        return [
            TOCEntry(
                id=section.id,
                title=section.title,
                level=section.level,
                page_number=section.page_number,
                children=[],
            )
            for section in sorted(sections, key=lambda s: s.order_index)
        ]

    def validate_hierarchy(self, sections: List[Section]) -> List[str]:
        """
        Validate section hierarchy and return list of issues.

        Checks:
        - No gaps in level progression (e.g., level 1 -> level 3 without level 2)
        - Proper parent-child relationships
        - Order_index consistency

        Args:
            sections: List of sections to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues: List[str] = []

        if not sections:
            return issues

        sorted_sections = sorted(sections, key=lambda s: s.order_index)

        # Check level progression
        prev_level = 0
        for i, section in enumerate(sorted_sections):
            # Check for level gaps (e.g., 1 -> 3)
            if section.level > prev_level + 1:
                issues.append(
                    f"Section '{section.title}' (level {section.level}) "
                    f"has gap in hierarchy after level {prev_level}"
                )

            # Check order_index is sequential
            if section.order_index != i:
                issues.append(
                    f"Section '{section.title}' has order_index {section.order_index} "
                    f"but expected {i}"
                )

            prev_level = section.level

        # Check parent relationships
        for section in sections:
            if section.parent_id:
                parent = self._section_map.get(section.parent_id)
                if not parent:
                    issues.append(
                        f"Section '{section.title}' references non-existent parent {section.parent_id}"
                    )
                elif parent.level >= section.level:
                    issues.append(
                        f"Section '{section.title}' (level {section.level}) "
                        f"has parent with same or greater level ({parent.level})"
                    )

        return issues

    def get_section_path(self, section_id: UUID, sections: List[Section]) -> List[str]:
        """
        Get breadcrumb path to a section (e.g., ["Chapter 1", "Section 1.2", "Subsection 1.2.3"]).

        Args:
            section_id: Target section ID
            sections: List of all sections

        Returns:
            List of section titles from root to target
        """
        self._section_map = {s.id: s for s in sections}

        path: List[str] = []
        current_id: Optional[UUID] = section_id

        # Walk up the parent chain
        while current_id:
            section = self._section_map.get(current_id)
            if not section:
                break

            path.insert(0, section.title)  # Add to front of list
            current_id = section.parent_id

        return path

    def count_sections_by_level(self, sections: List[Section]) -> Dict[int, int]:
        """
        Count sections grouped by level.

        Args:
            sections: List of sections

        Returns:
            Dictionary mapping level to count
        """
        counts: Dict[int, int] = {}

        for section in sections:
            counts[section.level] = counts.get(section.level, 0) + 1

        return counts

    def get_max_depth(self, entries: List[TOCEntry]) -> int:
        """
        Calculate maximum depth of TOC tree.

        Args:
            entries: List of TOC entries

        Returns:
            Maximum depth (1-based)
        """
        if not entries:
            return 0

        max_depth = 1

        for entry in entries:
            if entry.children:
                child_depth = self._get_depth_recursive(entry.children, 2)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _get_depth_recursive(self, entries: List[TOCEntry], current_depth: int) -> int:
        """
        Recursively calculate depth.

        Args:
            entries: Current level entries
            current_depth: Current depth counter

        Returns:
            Maximum depth from this point
        """
        max_depth = current_depth

        for entry in entries:
            if entry.children:
                child_depth = self._get_depth_recursive(
                    entry.children, current_depth + 1
                )
                max_depth = max(max_depth, child_depth)

        return max_depth

    def extract_chapter_headings(self, markdown_content: str, chapter_id: UUID) -> List[TOCEntry]:
        """
        Extract sub-headings from chapter markdown content.

        This method parses markdown headings (##, ###, ####) from chapter content
        and creates TOC entries for them. Useful for chapter-based documents
        where each chapter section contains nested headings.

        Args:
            markdown_content: Chapter markdown content
            chapter_id: Parent chapter section ID

        Returns:
            List of TOCEntry objects representing sub-headings
        """
        entries: List[TOCEntry] = []

        # Skip YAML frontmatter if present
        content = markdown_content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]

        # Find all markdown headings (## through ######)
        # Pattern: ^(###+)\s+(.+?)(?:\s+`\[p\.(\d+)\]`)?$
        heading_pattern = re.compile(
            r"^(#{2,6})\s+(.+?)(?:\s+`\[p\.(\d+)\]`)?$", re.MULTILINE
        )

        for match in heading_pattern.finditer(content):
            hashes = match.group(1)
            title = match.group(2).strip()
            page_str = match.group(3)

            # Calculate level (## is level 2, ### is level 3, etc.)
            level = len(hashes)
            page_number = int(page_str) if page_str else None

            entry = TOCEntry(
                id=f"{chapter_id}_{len(entries)}",  # Generate unique ID
                title=title,
                level=level,
                page_number=page_number,
                children=[],
            )
            entries.append(entry)

        # Build hierarchy from flat list
        if entries:
            return self._build_tree_from_entries(entries)

        return entries

    def _build_tree_from_entries(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """
        Build hierarchical tree from flat list of TOC entries.

        Args:
            entries: Flat list of TOC entries

        Returns:
            List of root entries with nested children
        """
        root_entries: List[TOCEntry] = []
        stack: List[TOCEntry] = []

        for entry in entries:
            # Pop stack until we find appropriate parent
            while stack and stack[-1].level >= entry.level:
                stack.pop()

            if stack:
                # Add as child to parent
                stack[-1].children.append(entry)
            else:
                # Root entry
                root_entries.append(entry)

            stack.append(entry)

        return root_entries
