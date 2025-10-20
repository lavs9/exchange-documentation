# Project Setup Checklist

Follow this checklist when setting up the project for the first time.

## Prerequisites Installation

### Required Software
- [ ] Docker (v20.10+): `docker --version`
- [ ] Docker Compose (v2.0+): `docker-compose --version`
- [ ] Git: `git --version`
- [ ] Code editor (VS Code recommended)

### Recommended VS Code Extensions
- [ ] Python (ms-python.python)
- [ ] Pylance (ms-python.vscode-pylance)
- [ ] ESLint (dbaeumer.vscode-eslint)
- [ ] Prettier (esbenp.prettier-vscode)
- [ ] Docker (ms-azuretools.vscode-docker)

## Initial Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd exchange-doc-manager
2. Environment Configuration
bash# Backend
cd backend
cp .env.example .env
# Edit .env with your configuration

# Frontend
cd ../frontend
cp .env.example .env
# Edit .env with your configuration
3. Start Services
bashcd ..
docker-compose up -d
4. Wait for Services to Initialize
bash# Check service health
docker-compose ps

# All services should show "healthy" or "running"
# This may take 30-60 seconds on first run
5. Run Database Migrations
bashdocker-compose exec backend alembic upgrade head
6. Verify Installation
bash# Check backend
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Check frontend
# Open browser: http://localhost:3000
# Should see upload interface

# Check API docs
# Open browser: http://localhost:8000/docs
# Should see Swagger UI
7. Load Sample Data (Optional)
bash# Upload NSE NNF Protocol v6.2 via UI
# Or use curl:
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@/path/to/NSE_NNF_Protocol_v6.2.pdf" \
  -F "title=NSE NNF Protocol" \
  -F "version=6.2"
Development Setup
Backend Development
bash# Enter backend container
docker-compose exec backend bash

# Install dev dependencies (if not in Dockerfile)
poetry install --with dev

# Run tests
pytest

# Format code
black app/

# Lint
ruff app/
Frontend Development
bash# Enter frontend container
docker-compose exec frontend sh

# Install dependencies (if needed)
npm install

# Run tests
npm test

# Lint
npm run lint
Troubleshooting
Port Conflicts
If ports 3000, 5432, or 8000 are in use:
bash# Check what's using ports
lsof -i :3000
lsof -i :5432
lsof -i :8000

# Option 1: Stop conflicting services
# Option 2: Change ports in docker-compose.yml
Database Connection Issues
bash# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
Container Build Failures
bash# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
Permission Issues (Linux/Mac)
bash# Fix uploads directory permissions
sudo chown -R $USER:$USER backend/uploads
Verification Tests
Backend Tests

 pytest runs successfully
 API docs accessible at http://localhost:8000/docs
 Health check returns 200
 Can upload a PDF file

Frontend Tests

 npm test runs successfully
 Application loads at http://localhost:3000
 Can click "Upload" button
 No console errors in browser

Integration Tests

 Upload NSE PDF → processes successfully
 TOC appears after processing
 Search returns results
 Can navigate to sections
 Can delete document

Next Steps
After successful setup:

Read .claude/architecture.md for system overview
Review .claude/conventions.md for coding standards
Check .claude/quick-reference.md for common commands
Start with a small feature using .claude/prompts/feature-implementation.md

Getting Help
If you encounter issues:

Check troubleshooting section above
Review Docker logs: docker-compose logs [service-name]
Search existing GitHub issues
Create new issue with .claude/prompts/bug-fix.md template