"""Service for parsing, resolving, and discovering wikilinks in markdown files."""
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WikiLink:
    """Represents a parsed wikilink."""
    target: str  # e.g., "order-validation-tips"
    anchor: Optional[str]  # e.g., "section-4-1"
    raw_text: str  # e.g., "[[order-validation-tips#section-4-1]]"


@dataclass
class Backlink:
    """Represents a backlink to a document."""
    source_file: str  # Relative path to source file
    source_title: str  # Title extracted from heading or filename
    snippet: str  # Context around the link (±100 chars)
    line_number: int  # Line number where link appears


@dataclass
class GraphNode:
    """Represents a node in the document link graph."""
    file_path: str  # Relative path to file
    file_type: str  # "chapter", "note", or "reference"
    title: str  # Document title
    links_to: List[str]  # List of filenames this document links to
    linked_from: List[str]  # List of filenames linking to this document (backlinks)


class WikiLinkError(Exception):
    """Base exception for wikilink operations."""
    pass


class WikiLinkService:
    """
    Service for managing wikilinks in markdown files.

    This service:
    - Parses [[wikilinks]] from markdown content
    - Resolves wikilink targets to file paths
    - Discovers backlinks (who links here?)
    - Builds link graphs for visualization
    """

    # Regex pattern for matching wikilinks: [[target]] or [[target#anchor]]
    WIKILINK_PATTERN = re.compile(r'\[\[([^\]#]+)(#[^\]]+)?\]\]')

    def __init__(self, base_path: str = "backend/storage/documents"):
        """
        Initialize WikiLinkService.

        Args:
            base_path: Base path to document storage
        """
        self._base_path = Path(base_path)

    def parse_wikilinks(self, content: str) -> List[WikiLink]:
        """
        Extract all [[wikilinks]] from markdown content.

        Args:
            content: Markdown content to parse

        Returns:
            List of WikiLink objects

        Example:
            >>> service.parse_wikilinks("See [[order-tips#validation]] for details")
            [WikiLink(target='order-tips', anchor='validation', raw_text='[[order-tips#validation]]')]
        """
        wikilinks = []
        for match in self.WIKILINK_PATTERN.finditer(content):
            target = match.group(1).strip()
            anchor = match.group(2).strip('#') if match.group(2) else None
            raw_text = match.group(0)

            wikilinks.append(WikiLink(
                target=target,
                anchor=anchor,
                raw_text=raw_text
            ))

        logger.debug(f"Parsed {len(wikilinks)} wikilinks from content")
        return wikilinks

    def resolve_link(self, link_target: str, base_path: str) -> Optional[str]:
        """
        Resolve wikilink target to actual file path.

        Searches in order:
        1. notes/{link_target}.md
        2. references/{link_target}.md
        3. chapters/{link_target}.md
        4. Recursive search in subdirectories

        Args:
            link_target: Target filename (without .md extension)
            base_path: Base path to search within (e.g., "storage/documents/nse-nnf/versions/v6.1")

        Returns:
            Relative file path or None if not found

        Example:
            >>> service.resolve_link("order-validation-tips", "storage/documents/nse-nnf/versions/v6.1")
            "notes/order-validation-tips.md"
        """
        search_base = Path(base_path)

        # Search order: notes, references, chapters
        search_paths = [
            search_base / "notes" / f"{link_target}.md",
            search_base / "references" / f"{link_target}.md",
            search_base / "chapters" / f"{link_target}.md",
        ]

        # Check direct paths first
        for path in search_paths:
            if path.exists():
                try:
                    rel_path = path.relative_to(search_base)
                    return str(rel_path)
                except ValueError:
                    continue

        # Recursive search in subdirectories
        for directory in ["notes", "references", "chapters"]:
            dir_path = search_base / directory
            if dir_path.exists():
                for md_file in dir_path.rglob(f"{link_target}.md"):
                    try:
                        rel_path = md_file.relative_to(search_base)
                        return str(rel_path)
                    except ValueError:
                        continue

        logger.warning(f"Could not resolve wikilink target: {link_target}")
        return None

    def get_backlinks(
        self,
        target_file: str,
        doc_path: str,
        snippet_chars: int = 100
    ) -> List[Backlink]:
        """
        Find all files that link to target_file.

        Args:
            target_file: Target file path (relative to doc_path)
            doc_path: Document version path to search within
            snippet_chars: Number of characters to extract around link for context

        Returns:
            List of Backlink objects

        Example:
            >>> service.get_backlinks("chapters/chapter-04-order-entry.md", "storage/.../v6.1")
            [Backlink(source_file='notes/order-tips.md', source_title='Order Tips', ...)]
        """
        backlinks = []
        search_base = Path(doc_path)
        target_path = search_base / target_file

        # Extract target filename without extension for matching
        target_name = Path(target_file).stem

        # Search all markdown files
        for md_file in search_base.rglob("*.md"):
            if md_file == target_path:
                continue  # Skip self-references

            try:
                content = md_file.read_text(encoding="utf-8")
                lines = content.split('\n')

                # Parse wikilinks in this file
                for line_num, line in enumerate(lines, start=1):
                    wikilinks = self.parse_wikilinks(line)

                    for wikilink in wikilinks:
                        # Resolve the wikilink to see if it points to our target
                        resolved = self.resolve_link(wikilink.target, str(search_base))

                        if resolved == target_file or wikilink.target == target_name:
                            # Extract title from file
                            title = self._extract_title(content, md_file.name)

                            # Build snippet with context
                            snippet = self._build_snippet(lines, line_num - 1, snippet_chars)

                            backlinks.append(Backlink(
                                source_file=str(md_file.relative_to(search_base)),
                                source_title=title,
                                snippet=snippet,
                                line_number=line_num
                            ))

            except Exception as e:
                logger.error(f"Error processing file {md_file}: {e}")
                continue

        logger.info(f"Found {len(backlinks)} backlinks to {target_file}")
        return backlinks

    def build_link_graph(self, doc_path: str) -> Dict[str, GraphNode]:
        """
        Build complete link graph for entire document version.

        Returns bidirectional graph with:
        - Outgoing links (links_to)
        - Incoming links (linked_from / backlinks)

        Args:
            doc_path: Document version path

        Returns:
            Dict mapping filename → GraphNode

        Example:
            >>> graph = service.build_link_graph("storage/.../v6.1")
            >>> graph["notes/order-tips.md"].links_to
            ['chapters/chapter-04-order-entry.md']
        """
        search_base = Path(doc_path)
        graph: Dict[str, GraphNode] = {}

        # First pass: build nodes and outgoing links
        for md_file in search_base.rglob("*.md"):
            try:
                rel_path = str(md_file.relative_to(search_base))
                content = md_file.read_text(encoding="utf-8")

                # Determine file type
                file_type = self._determine_file_type(rel_path)

                # Extract title
                title = self._extract_title(content, md_file.name)

                # Parse wikilinks to find outgoing links
                wikilinks = self.parse_wikilinks(content)
                links_to = []

                for wikilink in wikilinks:
                    resolved = self.resolve_link(wikilink.target, str(search_base))
                    if resolved:
                        links_to.append(resolved)

                # Create node
                graph[rel_path] = GraphNode(
                    file_path=rel_path,
                    file_type=file_type,
                    title=title,
                    links_to=list(set(links_to)),  # Remove duplicates
                    linked_from=[]  # Will be filled in second pass
                )

            except Exception as e:
                logger.error(f"Error processing file {md_file}: {e}")
                continue

        # Second pass: build backlinks (invert graph)
        for node_path, node in graph.items():
            for target in node.links_to:
                if target in graph:
                    graph[target].linked_from.append(node_path)

        logger.info(f"Built link graph with {len(graph)} nodes")
        return graph

    def _extract_title(self, content: str, fallback_filename: str) -> str:
        """
        Extract title from markdown content.

        Tries to extract from:
        1. YAML frontmatter (title field)
        2. First H1 heading (# Heading)
        3. Filename as fallback

        Args:
            content: Markdown content
            fallback_filename: Filename to use if no title found

        Returns:
            Extracted title
        """
        # Try YAML frontmatter
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if frontmatter_match:
            title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', frontmatter_match.group(1), re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()

        # Try first H1 heading
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        # Fallback to filename without extension
        return Path(fallback_filename).stem.replace('-', ' ').replace('_', ' ').title()

    def _build_snippet(self, lines: List[str], line_index: int, chars: int) -> str:
        """
        Build snippet with context around a specific line.

        Args:
            lines: All lines in file
            line_index: Index of line containing link (0-based)
            chars: Number of characters to extract before/after

        Returns:
            Snippet string
        """
        # Get the line with the link
        target_line = lines[line_index] if line_index < len(lines) else ""

        # Extract context before and after
        before = target_line[:chars]
        after = target_line[-chars:]

        # If line is short, include neighboring lines
        if len(target_line) < chars * 2:
            # Include previous line
            if line_index > 0:
                before = lines[line_index - 1][-chars:] + " " + target_line

            # Include next line
            if line_index < len(lines) - 1:
                after = target_line + " " + lines[line_index + 1][:chars]

        return f"...{before}...{after}..."

    def _determine_file_type(self, rel_path: str) -> str:
        """
        Determine file type from relative path.

        Args:
            rel_path: Relative file path

        Returns:
            "chapter", "note", or "reference"
        """
        if rel_path.startswith("chapters/"):
            return "chapter"
        elif rel_path.startswith("notes/"):
            return "note"
        elif rel_path.startswith("references/"):
            return "reference"
        else:
            return "unknown"
