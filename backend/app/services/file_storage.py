"""
File Storage Service

Centralized file system operations for markdown files, metadata, and directory management.
Follows the hybrid file-based architecture where content lives in files and metadata in DB.
"""
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FileStorageError(Exception):
    """Raised when file storage operations fail."""
    pass


class FileStorageService:
    """Manage file system operations for document storage."""

    def __init__(self, base_path: str = "storage/documents"):
        """
        Initialize file storage service.

        Args:
            base_path: Base directory for document storage
        """
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileStorageService initialized with base_path: {self._base_path}")

    def save_chapter(
        self,
        doc_slug: str,
        version: str,
        chapter_number: int,
        title: str,
        content: str,
    ) -> str:
        """
        Save chapter markdown to file.

        Args:
            doc_slug: Document slug (e.g., "nse-nnf-protocol")
            version: Version string (e.g., "v6.3")
            chapter_number: Chapter number
            title: Chapter title
            content: Markdown content

        Returns:
            Relative file path from base_path

        Raises:
            FileStorageError: If file write fails
        """
        try:
            # Ensure directory structure exists
            self.ensure_directory_structure(doc_slug, version)

            # Generate filename
            title_slug = self._slugify(title)
            filename = f"chapter-{chapter_number:02d}-{title_slug}.md"
            file_path = self._get_chapter_path(doc_slug, version) / filename

            # Write content to file
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved chapter {chapter_number} to {file_path}")

            # Return relative path
            return str(file_path.relative_to(self._base_path))

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to save chapter {chapter_number}: {e}") from e

    def read_chapter(self, file_path: str) -> str:
        """
        Read chapter content from file.

        Args:
            file_path: Relative path from base_path

        Returns:
            Markdown content with frontmatter stripped

        Raises:
            FileStorageError: If file not found or read fails
        """
        try:
            full_path = self._base_path / file_path
            self._validate_path(full_path)

            if not full_path.exists():
                raise FileStorageError(f"Chapter file not found: {file_path}")

            content = full_path.read_text(encoding="utf-8")

            # Strip YAML frontmatter if present
            content = self._strip_frontmatter(content)

            logger.debug(f"Read chapter from {file_path}")
            return content

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to read chapter from {file_path}: {e}") from e

    def _strip_frontmatter(self, content: str) -> str:
        """
        Strip YAML frontmatter from markdown content.

        Frontmatter is metadata between --- delimiters at the start of the file.

        Args:
            content: Raw markdown content

        Returns:
            Markdown content without frontmatter
        """
        if content.startswith("---"):
            # Find the closing ---
            parts = content.split("---", 2)
            if len(parts) >= 3:
                # parts[0] is empty, parts[1] is frontmatter, parts[2] is content
                return parts[2].lstrip()
        return content

    def save_metadata(
        self,
        doc_slug: str,
        version: str,
        metadata: Dict,
    ) -> str:
        """
        Save version metadata.json.

        Args:
            doc_slug: Document slug
            version: Version string
            metadata: Metadata dictionary

        Returns:
            Relative file path

        Raises:
            FileStorageError: If write fails
        """
        try:
            self.ensure_directory_structure(doc_slug, version)

            metadata_path = self._get_version_path(doc_slug, version) / "metadata.json"
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            logger.info(f"Saved metadata to {metadata_path}")

            return str(metadata_path.relative_to(self._base_path))

        except (OSError, IOError, json.JSONDecodeError) as e:
            raise FileStorageError(f"Failed to save metadata: {e}") from e

    def read_metadata(self, doc_slug: str, version: str) -> Dict:
        """
        Read version metadata.json.

        Args:
            doc_slug: Document slug
            version: Version string

        Returns:
            Metadata dictionary

        Raises:
            FileStorageError: If file not found or read fails
        """
        try:
            metadata_path = self._get_version_path(doc_slug, version) / "metadata.json"
            self._validate_path(metadata_path)

            if not metadata_path.exists():
                raise FileStorageError(f"Metadata file not found for {doc_slug}/{version}")

            content = metadata_path.read_text(encoding="utf-8")
            return json.loads(content)

        except (OSError, IOError, json.JSONDecodeError) as e:
            raise FileStorageError(f"Failed to read metadata: {e}") from e

    def get_active_version(self, doc_slug: str) -> Optional[str]:
        """
        Read active_version.txt.

        Args:
            doc_slug: Document slug

        Returns:
            Active version string or None if not set

        Raises:
            FileStorageError: If read fails
        """
        try:
            version_file = self._get_document_path(doc_slug) / "active_version.txt"

            if not version_file.exists():
                return None

            version = version_file.read_text(encoding="utf-8").strip()
            logger.debug(f"Active version for {doc_slug}: {version}")
            return version

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to read active version: {e}") from e

    def set_active_version(self, doc_slug: str, version: str) -> None:
        """
        Write active_version.txt.

        Args:
            doc_slug: Document slug
            version: Version string to set as active

        Raises:
            FileStorageError: If write fails
        """
        try:
            doc_path = self._get_document_path(doc_slug)
            doc_path.mkdir(parents=True, exist_ok=True)

            version_file = doc_path / "active_version.txt"
            version_file.write_text(version, encoding="utf-8")
            logger.info(f"Set active version for {doc_slug} to {version}")

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to set active version: {e}") from e

    def save_linked_doc(
        self,
        doc_slug: str,
        version: str,
        filename: str,
        content: str,
    ) -> str:
        """
        Save linked explanation document to links/ directory.

        Args:
            doc_slug: Document slug
            version: Version string
            filename: Filename for linked document
            content: Markdown content

        Returns:
            Relative file path

        Raises:
            FileStorageError: If write fails
        """
        try:
            self.ensure_directory_structure(doc_slug, version)

            links_path = self._get_version_path(doc_slug, version) / "links"
            links_path.mkdir(exist_ok=True)

            file_path = links_path / filename
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved linked document to {file_path}")

            return str(file_path.relative_to(self._base_path))

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to save linked document: {e}") from e

    def read_linked_doc(self, file_path: str) -> str:
        """
        Read linked document content.

        Args:
            file_path: Relative path from base_path

        Returns:
            Markdown content

        Raises:
            FileStorageError: If file not found or read fails
        """
        return self.read_chapter(file_path)  # Same implementation

    def list_linked_docs(self, doc_slug: str, version: str) -> List[str]:
        """
        List all linked documents for a version.

        Args:
            doc_slug: Document slug
            version: Version string

        Returns:
            List of relative file paths

        Raises:
            FileStorageError: If read fails
        """
        try:
            links_path = self._get_version_path(doc_slug, version) / "links"

            if not links_path.exists():
                return []

            files = [
                str(f.relative_to(self._base_path))
                for f in links_path.glob("*.md")
            ]
            logger.debug(f"Found {len(files)} linked documents for {doc_slug}/{version}")
            return sorted(files)

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to list linked documents: {e}") from e

    def copy_version_directory(
        self,
        doc_slug: str,
        from_version: str,
        to_version: str,
    ) -> None:
        """
        Copy entire version directory (for creating drafts).

        Args:
            doc_slug: Document slug
            from_version: Source version
            to_version: Target version

        Raises:
            FileStorageError: If copy fails
        """
        try:
            from_path = self._get_version_path(doc_slug, from_version)
            to_path = self._get_version_path(doc_slug, to_version)

            if not from_path.exists():
                raise FileStorageError(f"Source version not found: {from_version}")

            if to_path.exists():
                raise FileStorageError(f"Target version already exists: {to_version}")

            shutil.copytree(from_path, to_path)
            logger.info(f"Copied version directory from {from_version} to {to_version}")

        except (OSError, IOError, shutil.Error) as e:
            raise FileStorageError(f"Failed to copy version directory: {e}") from e

    def delete_version_directory(self, doc_slug: str, version: str) -> None:
        """
        Delete entire version directory.

        Args:
            doc_slug: Document slug
            version: Version string

        Raises:
            FileStorageError: If delete fails
        """
        try:
            version_path = self._get_version_path(doc_slug, version)

            if not version_path.exists():
                logger.warning(f"Version directory not found: {version_path}")
                return

            shutil.rmtree(version_path)
            logger.info(f"Deleted version directory: {version_path}")

        except (OSError, IOError, shutil.Error) as e:
            raise FileStorageError(f"Failed to delete version directory: {e}") from e

    def list_versions(self, doc_slug: str) -> List[str]:
        """
        List all versions for a document.

        Args:
            doc_slug: Document slug

        Returns:
            List of version strings

        Raises:
            FileStorageError: If read fails
        """
        try:
            versions_path = self._get_document_path(doc_slug) / "versions"

            if not versions_path.exists():
                return []

            versions = [d.name for d in versions_path.iterdir() if d.is_dir()]
            logger.debug(f"Found {len(versions)} versions for {doc_slug}")
            return sorted(versions)

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to list versions: {e}") from e

    def ensure_directory_structure(self, doc_slug: str, version: str) -> None:
        """
        Create directory structure if it doesn't exist.

        Structure:
        storage/documents/{doc-slug}/versions/{version}/
            chapters/
            links/
            diffs/

        Args:
            doc_slug: Document slug
            version: Version string

        Raises:
            FileStorageError: If directory creation fails
        """
        try:
            version_path = self._get_version_path(doc_slug, version)
            version_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            (version_path / "chapters").mkdir(exist_ok=True)
            (version_path / "links").mkdir(exist_ok=True)
            (version_path / "diffs").mkdir(exist_ok=True)

            logger.debug(f"Ensured directory structure for {doc_slug}/{version}")

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to create directory structure: {e}") from e

    def save_user_document(
        self,
        doc_slug: str,
        version: str,
        directory: str,
        filename: str,
        content: str,
    ) -> str:
        """
        Save user-created document (note or reference) to file.

        Args:
            doc_slug: Document slug
            version: Version string
            directory: "notes" or "references"
            filename: Filename (e.g., "order-validation-tips.md")
            content: Markdown content

        Returns:
            Relative file path from base_path

        Raises:
            FileStorageError: If write fails
        """
        try:
            self.ensure_directory_structure(doc_slug, version)

            # Create directory if doesn't exist
            dir_path = self._get_version_path(doc_slug, version) / directory
            dir_path.mkdir(exist_ok=True)

            # Ensure unique filename
            file_path = dir_path / filename
            counter = 1
            base_name = Path(filename).stem
            extension = Path(filename).suffix

            while file_path.exists():
                new_filename = f"{base_name}-{counter}{extension}"
                file_path = dir_path / new_filename
                counter += 1

            # Write content
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Saved user document to {file_path}")

            return str(file_path.relative_to(self._base_path))

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to save user document: {e}") from e

    def read_user_document(self, file_path: str) -> str:
        """
        Read user document content from file.

        Args:
            file_path: Relative path from base_path

        Returns:
            Markdown content

        Raises:
            FileStorageError: If file not found or read fails
        """
        try:
            full_path = self._base_path / file_path
            self._validate_path(full_path)

            if not full_path.exists():
                raise FileStorageError(f"User document not found: {file_path}")

            content = full_path.read_text(encoding="utf-8")
            logger.debug(f"Read user document from {file_path}")
            return content

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to read user document: {e}") from e

    def update_user_document(self, file_path: str, content: str) -> None:
        """
        Update user document content.

        Args:
            file_path: Relative path from base_path
            content: New markdown content

        Raises:
            FileStorageError: If file not found or write fails
        """
        try:
            full_path = self._base_path / file_path
            self._validate_path(full_path)

            if not full_path.exists():
                raise FileStorageError(f"User document not found: {file_path}")

            full_path.write_text(content, encoding="utf-8")
            logger.info(f"Updated user document at {file_path}")

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to update user document: {e}") from e

    def delete_user_document(self, file_path: str) -> None:
        """
        Delete user document file.

        Args:
            file_path: Relative path from base_path

        Raises:
            FileStorageError: If delete fails
        """
        try:
            full_path = self._base_path / file_path
            self._validate_path(full_path)

            if full_path.exists():
                full_path.unlink()
                logger.info(f"Deleted user document at {file_path}")
            else:
                logger.warning(f"User document not found for deletion: {file_path}")

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to delete user document: {e}") from e

    def move_user_document(self, old_path: str, new_path: str) -> None:
        """
        Rename/move user document file.

        Args:
            old_path: Current relative path from base_path
            new_path: New relative path from base_path

        Raises:
            FileStorageError: If move fails
        """
        try:
            old_full_path = self._base_path / old_path
            new_full_path = self._base_path / new_path

            self._validate_path(old_full_path)
            self._validate_path(new_full_path)

            if not old_full_path.exists():
                raise FileStorageError(f"Source file not found: {old_path}")

            # Create parent directories if needed
            new_full_path.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            old_full_path.rename(new_full_path)
            logger.info(f"Moved user document from {old_path} to {new_path}")

        except (OSError, IOError) as e:
            raise FileStorageError(f"Failed to move user document: {e}") from e

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_document_path(self, doc_slug: str) -> Path:
        """Get path to document directory."""
        return self._base_path / doc_slug

    def _get_version_path(self, doc_slug: str, version: str) -> Path:
        """Get path to version directory."""
        return self._get_document_path(doc_slug) / "versions" / version

    def _get_chapter_path(self, doc_slug: str, version: str) -> Path:
        """Get path to chapters directory."""
        return self._get_version_path(doc_slug, version) / "chapters"

    def _slugify(self, text: str) -> str:
        """
        Convert text to filename-safe slug.

        Args:
            text: Text to slugify

        Returns:
            Slugified string (lowercase, hyphens, alphanumeric)
        """
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and underscores with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        # Remove non-alphanumeric characters (keep hyphens)
        text = re.sub(r'[^a-z0-9-]', '', text)
        # Remove duplicate hyphens
        text = re.sub(r'-+', '-', text)
        # Strip leading/trailing hyphens
        text = text.strip('-')
        # Limit length
        return text[:50]

    def _validate_path(self, path: Path) -> None:
        """
        Validate that path is within base_path (prevent directory traversal).

        Args:
            path: Path to validate

        Raises:
            FileStorageError: If path is outside base_path
        """
        try:
            path.resolve().relative_to(self._base_path.resolve())
        except ValueError:
            raise FileStorageError(f"Invalid path: {path} (outside base directory)")
