# New Architecture: Decoupled Docling Processing

## Overview

The Exchange Documentation Manager now uses a **fully decoupled architecture** where Docling PDF processing is done **externally** from the main application.

## Architecture

```
┌─────────────────────────────────────┐
│   External Docling Processing      │
│   (Manual / Separate Script)       │
│                                     │
│   Input:  PDF                       │
│   Output: JSON, MD, HTML            │
└─────────────────────────────────────┘
            │
            ↓ Pre-processed files
┌─────────────────────────────────────┐
│   Document Management App           │
│   (FastAPI Backend)                 │
│                                     │
│   Input:  PDF + Docling JSON/MD     │
│   Process: Parse structure          │
│           Extract sections          │
│           Build TOC                 │
│           Index for search          │
│   Output: Structured DB             │
└─────────────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────┐
│   PostgreSQL Database               │
│   - Documents                       │
│   - Sections (hierarchical)         │
│   - Full-text search indexes        │
└─────────────────────────────────────┘
```

## Benefits

✅ **No Dependencies** - App doesn't need Docling library (500MB+ removed)
✅ **No Crashes** - No OOM issues from PDF processing
✅ **Instant Startup** - Backend starts immediately
✅ **Faster Processing** - No model downloads, no CPU-intensive work
✅ **Clean Separation** - PDF→JSON conversion is separate concern
✅ **Flexible** - Can use any Docling version/config externally

## Upload Endpoint (New)

### POST `/api/documents/upload`

**Request (multipart/form-data)**:
- `pdf_file`: Original PDF (required)
- `docling_json`: Docling JSON output (optional)
- `docling_md`: Docling Markdown output (optional)
- `title`: Document title (required)
- `version`: Document version (required)

**Note**: Must provide either `docling_json` OR `docling_md` (or both)

**Response**:
```json
{
  "id": "uuid",
  "title": "NSE CM API",
  "version": "v6.2",
  "processing_status": "processing",
  "upload_date": "2025-01-08T10:00:00Z",
  "file_path": "/app/uploads/NSE_CM_API_v6.2_20250108_100000.pdf",
  "page_count": null
}
```

## Example Usage

### Using cURL

```bash
# Upload PDF with Docling JSON
curl -X POST http://localhost:8000/api/documents/upload \
  -F "pdf_file=@document.pdf" \
  -F "docling_json=@document.json" \
  -F "title=NSE CM API" \
  -F "version=v6.2"

# Upload PDF with Docling Markdown
curl -X POST http://localhost:8000/api/documents/upload \
  -F "pdf_file=@document.pdf" \
  -F "docling_md=@document.md" \
  -F "title=NSE CM API" \
  -F "version=v6.2"

# Upload PDF with both
curl -X POST http://localhost:8000/api/documents/upload \
  -F "pdf_file=@document.pdf" \
  -F "docling_json=@document.json" \
  -F "docling_md=@document.md" \
  -F "title=NSE CM API" \
  -F "version=v6.2"
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/documents/upload"

files = {
    "pdf_file": ("document.pdf", open("document.pdf", "rb"), "application/pdf"),
    "docling_json": ("document.json", open("document.json", "rb"), "application/json"),
}

data = {
    "title": "NSE CM API",
    "version": "v6.2",
}

response = requests.post(url, files=files, data=data)
document = response.json()

print(f"Document ID: {document['id']}")
print(f"Status: {document['processing_status']}")
```

## Docling JSON Parser

The app now uses `DoclingJSONParser` which supports:

### JSON Format

Expects Docling JSON with structure like:
```json
{
  "num_pages": 10,
  "main-text": [
    {
      "type": "title",
      "text": "Document Title",
      "page": 1
    },
    {
      "type": "section-header",
      "text": "Section 1",
      "page": 1
    },
    {
      "type": "paragraph",
      "text": "Content here...",
      "page": 1
    }
  ]
}
```

### Markdown Format

Standard markdown with headings:
```markdown
# Document Title

## Section 1

Content here...

### Subsection 1.1

More content...
```

## File Storage

Files are stored in the uploads directory:

```
/app/uploads/
├── Document_Title_v6.2_20250108_100000.pdf     # Original PDF
├── Document_Title_v6.2_20250108_100000.json    # Docling JSON (if provided)
└── Document_Title_v6.2_20250108_100000.md      # Docling MD (if provided)
```

## Processing Flow

1. **Upload** - User uploads PDF + Docling output files
2. **Save Files** - All files saved to disk with same basename
3. **Queue Processing** - Background task queued
4. **Parse Docling Output** - JSON or MD parsed into sections
5. **Extract Hierarchy** - Section levels and parent relationships
6. **Save to DB** - Sections saved with full-text search indexes
7. **Update Status** - Document status → "completed"

## External Docling Processing

You have two options for processing PDFs with Docling:

### Option 1: Docling Serve (Recommended for Production)

Use the Docling Serve Docker container:

```bash
# Start Docling Serve
docker run -p 5001:5001 quay.io/docling-project/docling-serve:latest

# Convert PDF via API
curl -X POST http://localhost:5001/v1/convert/file \
  -F "files=@document.pdf" \
  -F "to_formats=md" \
  -F "to_formats=json" \
  > output.json

# Extract outputs
cat output.json | jq '.document.md' > document.md
cat output.json | jq '.document' > document.json
```

### Option 2: Docling Python Library (Local)

Use Docling library locally:

```python
from docling.document_converter import DocumentConverter, DocumentConversionInput
from pathlib import Path

# Initialize converter
converter = DocumentConverter()

# Convert PDF
input_doc = DocumentConversionInput.from_paths([Path("document.pdf")])
result_generator = converter.convert(input_doc)
result = next(iter(result_generator))

# Export to formats
markdown = result.document.export_to_markdown()
json_data = result.document.export_to_dict()

# Save outputs
with open("document.md", "w") as f:
    f.write(markdown)

import json
with open("document.json", "w") as f:
    json.dump(json_data, f, indent=2)
```

### Option 3: Batch Processing Script

Create a simple batch script:

```bash
#!/bin/bash
# process_pdfs.sh

DOCLING_URL="http://localhost:5001"

for pdf in pdfs/*.pdf; do
    base=$(basename "$pdf" .pdf)

    echo "Processing: $pdf"

    # Call Docling Serve
    curl -X POST "$DOCLING_URL/v1/convert/file" \
      -F "files=@$pdf" \
      -F "to_formats=md" \
      -F "to_formats=json" \
      -o "output/$base.json"

    # Extract markdown
    jq -r '.document.md' "output/$base.json" > "output/$base.md"

    echo "Done: output/$base.{json,md}"
done
```

## Migration Guide

### From Old Architecture

**Old** (Embedded Docling):
```bash
# Just upload PDF
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.pdf" \
  -F "title=NSE CM API" \
  -F "version=v6.2"
```

**New** (Pre-processed):
```bash
# 1. Process with Docling externally
docker run -p 5001:5001 quay.io/docling-project/docling-serve:latest &
curl -X POST http://localhost:5001/v1/convert/file \
  -F "files=@document.pdf" > docling_output.json

# 2. Extract markdown
jq -r '.document.md' docling_output.json > document.md

# 3. Upload to app
curl -X POST http://localhost:8000/api/documents/upload \
  -F "pdf_file=@document.pdf" \
  -F "docling_md=@document.md" \
  -F "title=NSE CM API" \
  -F "version=v6.2"
```

## Testing

### Quick Test with Sample File

```bash
# 1. Create a simple markdown file
cat > test.md << 'EOF'
# Test Document

## Section 1

This is section 1 content.

### Subsection 1.1

More content here.

## Section 2

Another section.
EOF

# 2. Create a dummy PDF
echo "PDF placeholder" > test.pdf

# 3. Upload
curl -X POST http://localhost:8000/api/documents/upload \
  -F "pdf_file=@test.pdf" \
  -F "docling_md=@test.md" \
  -F "title=Test Document" \
  -F "version=v1.0" | jq

# 4. Check status
curl http://localhost:8000/api/documents | jq
```

## Troubleshooting

### Error: "Either docling_json or docling_md file is required"

**Cause**: No Docling output file provided

**Solution**: Include `-F "docling_json=@file.json"` or `-F "docling_md=@file.md"`

### Error: "No Docling output found"

**Cause**: Files saved but processing can't find .json or .md

**Solution**: Check that files are saved with correct extensions in uploads directory

### Processing Stuck at "processing"

**Cause**: Error in parsing Docling output

**Solution**: Check logs with `docker-compose logs backend | tail -100`

## Next Steps

1. **For Development**: Use simple markdown files for testing
2. **For Production**: Set up Docling Serve separately
3. **For CI/CD**: Add Docling processing to pipeline

## Future Enhancements

- [ ] Add batch upload endpoint (multiple PDFs at once)
- [ ] Support direct Docling Serve integration (optional)
- [ ] Add retry mechanism for failed parses
- [ ] Support HTML output from Docling
- [ ] Add validation for Docling JSON schema

---

**Last Updated**: January 8, 2025
**Architecture Version**: 2.0 (Decoupled)
