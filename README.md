cat > README.md << 'EOF'
# Exchange API Documentation Manager

Transform NSE API PDFs into searchable, navigable documentation.

## Quick Start
```bash
docker-compose up -d

Frontend: http://localhost:3000
Backend API: http://localhost:8000/docs

Documentation

Setup Guide
Architecture
Contributing
Quick Reference

Phase 1 Features

✅ PDF upload and parsing
✅ Auto-generated table of contents
✅ Full-text search
✅ Markdown document viewer

Development
See Quick Reference for common commands.
EOF

### Backend `.env.example`
```bash
mkdir -p backend
cat > backend/.env.example << 'EOF'
DATABASE_URL=postgresql://docuser:docpass@postgres:5432/exchange_docs
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=50
LOG_LEVEL=INFO
EOF
Frontend .env.example
bashmkdir -p frontend
cat > frontend/.env.example << 'EOF'
VITE_API_URL=http://localhost:8000
EOF