"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Exchange Documentation Manager API")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down Exchange Documentation Manager API")
    await engine.dispose()


app = FastAPI(
    title="Exchange Documentation Manager API",
    description="API for managing and searching NSE exchange documentation",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Exchange Documentation Manager API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# Import and include routers
# Use v2 API with file-based storage
from app.api import documents_v2, search, user_documents

app.include_router(documents_v2.router, prefix="/api/documents", tags=["documents"])
app.include_router(user_documents.router, prefix="/api/documents", tags=["user-documents"])
app.include_router(search.router, prefix="/api", tags=["search"])
