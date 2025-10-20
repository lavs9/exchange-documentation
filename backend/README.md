# Exchange Documentation Manager - Backend

FastAPI-based backend for managing and searching NSE exchange documentation.

## Features

- **Document Management**: Upload, list, view, and delete PDF documents
- **PDF Processing**: Extract structured content using Docling
- **Full-Text Search**: PostgreSQL-powered search with ranking
- **Table of Contents**: Auto-generated hierarchical TOC
- **RESTful API**: OpenAPI/Swagger documentation

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15 with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **PDF Processing**: Docling
- **Dependency Management**: Poetry (dev) / pip (Docker)
- **Type Checking**: mypy (strict mode)
- **Code Formatting**: Black
- **Linting**: Ruff

## Project Structure

```
backend/
├── app/
│   ├── api/                # API endpoints
│   │   ├── dependencies.py # Shared dependencies
│   │   └── documents.py    # Document endpoints
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings
│   │   └── database.py     # Database connection
│   ├── models/             # SQLAlchemy models
│   │   ├── document.py
│   │   └── section.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── document.py
│   │   └── search.py
│   ├── services/           # Business logic
│   │   └── document_processor.py
│   └── main.py             # FastAPI app
├── tests/                  # Test suite
├── alembic/                # Database migrations
├── Dockerfile
├── pyproject.toml          # Poetry dependencies (for local dev)
├── requirements.txt        # Pip dependencies (for Docker)
├── requirements-dev.txt    # Dev dependencies
└── README.md
```

## Quick Start

### Using Docker Compose (Recommended)

From the project root:

```bash
docker-compose up --build
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Local Development

1. **Install Poetry**:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install dependencies**:
```bash
cd backend
poetry install
```

3. **Set up environment variables**:
```bash
cp ../.env.example .env
# Edit .env with your settings
```

4. **Run PostgreSQL**:
```bash
docker run -d \
  --name exchange-doc-db \
  -e POSTGRES_DB=exchange_docs \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

5. **Run migrations**:
```bash
poetry run alembic upgrade head
```

**Note**: If using Docker Compose, migrations are automatically applied via `init.sql`. For production or local development, use Alembic migrations.

6. **Start the server**:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Documents

- `POST /api/documents/upload` - Upload a PDF document
- `GET /api/documents` - List all documents (paginated)
- `GET /api/documents/{id}` - Get document by ID
- `DELETE /api/documents/{id}` - Delete a document
- `GET /api/documents/{id}/status` - Check processing status
- `GET /api/documents/{id}/toc` - Get table of contents

### Health

- `GET /health` - Health check endpoint
- `GET /` - API info

## Development

### Code Style

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type check
poetry run mypy app/
```

### Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html
```

### Database Migrations

```bash
# Create new migration (auto-generate from model changes)
poetry run alembic revision --autogenerate -m "description"

# Create empty migration
poetry run alembic revision -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history

# Check current version
poetry run alembic current
```

See [alembic/README.md](alembic/README.md) for detailed migration documentation.

## Environment Variables

See `.env.example` in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/exchange_docs
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=52428800  # 50MB
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Database Schema

### documents
- `id` (UUID, PK)
- `title` (VARCHAR)
- `version` (VARCHAR)
- `upload_date` (TIMESTAMP)
- `file_path` (VARCHAR)
- `page_count` (INTEGER)
- `processing_status` (VARCHAR)
- `metadata` (JSONB)

### sections
- `id` (UUID, PK)
- `document_id` (UUID, FK)
- `level` (INTEGER)
- `title` (VARCHAR)
- `content` (TEXT)
- `page_number` (INTEGER)
- `parent_id` (UUID, FK)
- `order_index` (INTEGER)
- `search_vector` (TSVECTOR) - Generated column for FTS

## Performance

- Connection pooling: 5-10 connections
- File upload limit: 50MB
- Search response: < 500ms target
- PDF processing: < 2 minutes for 300-page document

## Future Enhancements

- [ ] Implement PDF parsing with Docling
- [ ] Add search endpoints
- [ ] Implement TOC generation
- [ ] Add background task processing
- [ ] Implement rate limiting
- [ ] Add API authentication

## Contributing

1. Follow the coding conventions in `.claude/conventions.md`
2. Use type hints for all functions
3. Add docstrings for public methods
4. Run tests before committing
5. Format code with Black

## License

Proprietary - Internal use only
