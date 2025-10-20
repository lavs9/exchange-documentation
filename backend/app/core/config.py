"""Application configuration using Pydantic Settings."""
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/exchange_docs",
        description="PostgreSQL database URL",
    )

    # File Upload
    upload_dir: Path = Field(
        default=Path("uploads"),
        description="Directory for uploaded files",
    )
    max_upload_size: int = Field(
        default=52428800,  # 50MB
        description="Maximum upload file size in bytes",
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Pagination
    default_page_size: int = Field(
        default=20,
        description="Default number of items per page",
    )
    max_page_size: int = Field(
        default=100,
        description="Maximum number of items per page",
    )

    # Search
    search_result_snippet_size: int = Field(
        default=50,
        description="Number of words in search result snippets",
    )


settings = Settings()

# Ensure upload directory exists
settings.upload_dir.mkdir(parents=True, exist_ok=True)
