"""Service for rendering chapters with resolved wikilinks and backlinks."""
import logging
import re
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from app.services.wikilink_service import WikiLinkService, Backlink
from app.services.file_storage import FileStorageService, FileStorageError

logger = logging.getLogger(__name__)


@dataclass
class HeadingNode:
    """Represents a heading in the outline."""
    level: int
    text: str
    anchor: str


@dataclass
class ChapterWithLinks:
    """Chapter content with resolved links and backlinks."""
    content: str  # Original markdown
    content_with_resolved_links: str  # Wikilinks converted to URLs
    backlinks: List[Dict]  # Who links here
    outline: List[Dict]  # TOC from headings
    metadata: Dict  # YAML frontmatter


class ChapterRenderError(Exception):
    """Base exception for chapter rendering operations."""
    pass


class ChapterRenderService:
    """
    Service for rendering chapters with wikilinks and backlinks.

    Provides:
    - Resolved wikilinks (convert [[links]] to markdown [links](urls))
    - Backlink discovery
    - Outline/TOC extraction
    - Frontmatter parsing
    """

    def __init__(
        self,
        wikilink_service: Optional[WikiLinkService] = None,
        file_storage: Optional[FileStorageService] = None
    ):
        """
        Initialize ChapterRenderService.

        Args:
            wikilink_service: WikiLink service (creates default if not provided)
            file_storage: File storage service (creates default if not provided)
        """
        self._wikilink_service = wikilink_service or WikiLinkService()
        self._file_storage = file_storage or FileStorageService()

    def render_chapter(
        self,
        chapter_file_path: str,
        doc_path: str,
        include_backlinks: bool = True,
        resolve_links: bool = True
    ) -> ChapterWithLinks:
        """
        Render chapter with resolved wikilinks and backlinks.

        Args:
            chapter_file_path: Relative path to chapter file
            doc_path: Document version base path (e.g., "storage/documents/nse-nnf/versions/v6.1")
            include_backlinks: Whether to discover backlinks
            resolve_links: Whether to resolve [[wikilinks]] to URLs

        Returns:
            ChapterWithLinks with all enriched data

        Raises:
            ChapterRenderError: If rendering fails
        """
        try:
            # Read chapter content
            content = self._file_storage.read_chapter(chapter_file_path)

            # Parse frontmatter
            metadata = self._parse_frontmatter(content)

            # Extract outline from headings
            outline = self._extract_outline(content)

            # Resolve wikilinks to URLs if requested
            content_with_resolved_links = content
            if resolve_links:
                content_with_resolved_links = self._resolve_wikilinks_to_urls(
                    content,
                    doc_path
                )

            # Get backlinks if requested
            backlinks = []
            if include_backlinks:
                backlinks_data = self._wikilink_service.get_backlinks(
                    target_file=chapter_file_path,
                    doc_path=doc_path
                )
                backlinks = [self._backlink_to_dict(bl) for bl in backlinks_data]

            return ChapterWithLinks(
                content=content,
                content_with_resolved_links=content_with_resolved_links,
                backlinks=backlinks,
                outline=[self._heading_to_dict(h) for h in outline],
                metadata=metadata
            )

        except FileStorageError as e:
            raise ChapterRenderError(f"Failed to read chapter: {e}") from e
        except Exception as e:
            raise ChapterRenderError(f"Failed to render chapter: {e}") from e

    def _resolve_wikilinks_to_urls(self, content: str, base_path: str) -> str:
        """
        Convert [[wikilinks]] to markdown [links](urls).

        Examples:
            [[order-validation-tips]] → [order-validation-tips](/api/notes/order-validation-tips)
            [[chapter-04#section-4-1]] → [Chapter 4, Section 4.1](/api/chapters/4#section-4-1)

        Args:
            content: Markdown content with wikilinks
            base_path: Document version path for link resolution

        Returns:
            Content with wikilinks replaced by markdown links
        """
        def replace_wikilink(match):
            raw_link = match.group(0)
            target = match.group(1).strip()
            anchor = match.group(2).strip('#') if match.group(2) else None

            # Resolve the link to find actual file
            resolved_path = self._wikilink_service.resolve_link(target, base_path)

            if not resolved_path:
                # Link not found, leave as-is or mark broken
                return f"[{target}](#broken-link)"

            # Determine URL based on file type
            if resolved_path.startswith("chapters/"):
                # Extract chapter number if possible
                chapter_match = re.search(r'chapter-(\d+)', resolved_path)
                chapter_num = chapter_match.group(1) if chapter_match else target

                url = f"/api/chapters/{chapter_num}"
                display_text = f"Chapter {chapter_num}"

                if anchor:
                    url += f"#{anchor}"
                    display_text += f", {anchor.replace('-', ' ').title()}"

            elif resolved_path.startswith("notes/"):
                filename = Path(resolved_path).stem
                url = f"/api/notes/{filename}"
                display_text = target.replace('-', ' ').title()

                if anchor:
                    url += f"#{anchor}"

            elif resolved_path.startswith("references/"):
                filename = Path(resolved_path).stem
                url = f"/api/references/{filename}"
                display_text = target.replace('-', ' ').title()

                if anchor:
                    url += f"#{anchor}"

            else:
                # Unknown type, generic link
                url = f"/api/documents/{target}"
                display_text = target

            return f"[{display_text}]({url})"

        # Replace all wikilinks
        resolved_content = self._wikilink_service.WIKILINK_PATTERN.sub(
            replace_wikilink,
            content
        )

        return resolved_content

    def _parse_frontmatter(self, content: str) -> Dict:
        """
        Extract YAML frontmatter from markdown content.

        Frontmatter is content between --- markers at the start of the file.

        Args:
            content: Markdown content

        Returns:
            Dictionary of frontmatter data (empty if no frontmatter)
        """
        # Match YAML frontmatter (--- ... ---)
        frontmatter_pattern = re.compile(
            r'^---\s*\n(.*?)\n---\s*\n',
            re.DOTALL | re.MULTILINE
        )

        match = frontmatter_pattern.match(content)
        if not match:
            return {}

        try:
            yaml_content = match.group(1)
            metadata = yaml.safe_load(yaml_content)
            return metadata or {}
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML frontmatter: {e}")
            return {}

    def _extract_outline(self, content: str) -> List[HeadingNode]:
        """
        Extract outline/TOC from markdown headings.

        Args:
            content: Markdown content

        Returns:
            List of HeadingNode objects
        """
        outline = []

        # Match markdown headings (# Heading, ## Subheading, etc.)
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

        for match in heading_pattern.finditer(content):
            level = len(match.group(1))  # Number of # symbols
            text = match.group(2).strip()

            # Generate anchor (slugify heading text)
            anchor = self._slugify_heading(text)

            outline.append(HeadingNode(
                level=level,
                text=text,
                anchor=anchor
            ))

        return outline

    def _slugify_heading(self, text: str) -> str:
        """
        Convert heading text to anchor-safe slug.

        Args:
            text: Heading text

        Returns:
            Slugified anchor string
        """
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remove non-alphanumeric characters (keep hyphens)
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # Remove duplicate hyphens
        slug = re.sub(r'-+', '-', slug)
        # Strip leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def _backlink_to_dict(self, backlink: Backlink) -> Dict:
        """Convert Backlink dataclass to dictionary."""
        return {
            "source_file": backlink.source_file,
            "source_title": backlink.source_title,
            "snippet": backlink.snippet,
            "line_number": backlink.line_number
        }

    def _heading_to_dict(self, heading: HeadingNode) -> Dict:
        """Convert HeadingNode dataclass to dictionary."""
        return {
            "level": heading.level,
            "text": heading.text,
            "anchor": heading.anchor
        }
