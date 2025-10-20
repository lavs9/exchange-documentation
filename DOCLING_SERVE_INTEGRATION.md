# Docling Serve Integration

## Overview

The Exchange API Documentation Manager now uses **Docling Serve** as an external microservice for PDF parsing, instead of the embedded Docling library. This architecture provides significant benefits:

✅ **No model downloads** - Models are pre-cached in the Docling Serve Docker image
✅ **Faster startup** - Backend starts immediately without waiting for ML model initialization
✅ **No crashes** - CPU/memory-intensive PDF processing happens in isolated container
✅ **Scalable** - Can run multiple Docling Serve instances for parallel processing
✅ **Cleaner separation** - PDF parsing is completely decoupled from API server

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   Client    │         │   Backend API    │         │  Docling Serve   │
│             │         │   (FastAPI)      │         │   (Microservice) │
└─────────────┘         └──────────────────┘         └──────────────────┘
      │                          │                            │
      │ POST /upload             │                            │
      ├─────────────────────────>│                            │
      │                          │                            │
      │ 202 ACCEPTED             │                            │
      │ {id, status:processing}  │                            │
      │<─────────────────────────┤                            │
      │                          │                            │
      │                          │ POST /v1/convert/file      │
      │                          ├───────────────────────────>│
      │                          │ (PDF file upload)          │
      │                          │                            │
      │                          │                     [Processing PDF]
      │                          │                     - Layout analysis
      │                          │                     - OCR (if needed)
      │                          │                     - Table extraction
      │                          │                     - Markdown export
      │                          │                            │
      │                          │ 200 OK                     │
      │                          │ {document: {md: "..."}}    │
      │                          │<───────────────────────────┤
      │                          │                            │
      │                    [Extract sections]                 │
      │                    [Save to database]                 │
      │                    [Update status]                    │
      │                          │                            │
      │ GET /status              │                            │
      ├─────────────────────────>│                            │
      │ {status: "completed"}    │                            │
      │<─────────────────────────┤                            │
```

## Docker Compose Setup

### Services

```yaml
services:
  docling-serve:
    image: quay.io/docling-project/docling-serve:latest
    ports:
      - "5001:5001"
    environment:
      DOCLING_SERVE_ENABLE_UI: 1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  backend:
    environment:
      DOCLING_SERVE_URL: http://docling-serve:5001
    depends_on:
      docling-serve:
        condition: service_healthy
```

### Image Sizes

- **Docling Serve (CPU)**: ~4.5 GB
- **Backend (without Docling library)**: ~500 MB

Total: ~5 GB (vs ~5.5 GB with embedded Docling + models)

## API Integration

### PDF Parser Implementation

**File**: `backend/app/services/pdf_parser_serve.py`

```python
class PDFParser:
    """PDF parser using Docling Serve API."""

    def __init__(self):
        self.docling_url = settings.docling_serve_url

    async def parse_pdf(self, file_path: Path) -> tuple[List[ParsedSection], int]:
        # Call Docling Serve API
        markdown_content, page_count = await self._convert_pdf_via_api(file_path)

        # Parse markdown into sections
        sections = self._parse_markdown_sections(markdown_content)

        return sections, page_count

    async def _convert_pdf_via_api(self, file_path: Path) -> tuple[str, int]:
        async with httpx.AsyncClient(timeout=300.0) as client:
            with open(file_path, "rb") as f:
                files = {"files": (file_path.name, f, "application/pdf")}

                response = await client.post(
                    f"{self.docling_url}/v1/convert/file",
                    files=files,
                    data={"to_formats": ["md"]},
                )

                response.raise_for_status()

        result = response.json()
        markdown = result["document"]["md"]

        return markdown, page_count
```

### Key Changes from Embedded Docling

| Aspect | Before (Embedded) | After (Docling Serve) |
|--------|-------------------|------------------------|
| **Import** | `from docling.document_converter import DocumentConverter` | `import httpx` |
| **Dependencies** | `docling>=1.0.0` (~500MB+ with models) | `httpx>=0.27.0` (~2MB) |
| **Initialization** | Lazy DocumentConverter (downloads models on first use) | API client (instant) |
| **Processing** | `converter.convert(path)` in thread pool | `async HTTP POST` to microservice |
| **First run** | 5-10 min model download | Immediate (models pre-cached) |
| **Subsequent runs** | 1-2 min per PDF | 30-60 sec per PDF |
| **Crash risk** | High (OOM, model loading issues) | Low (isolated service) |

## Docling Serve API

### Endpoint: `POST /v1/convert/file`

**Request**:
```http
POST /v1/convert/file HTTP/1.1
Host: docling-serve:5001
Content-Type: multipart/form-data

files: <PDF binary>
to_formats: ["md"]
```

**Optional Parameters**:
- `do_ocr`: boolean (default: true)
- `force_ocr`: boolean (default: false)
- `ocr_engine`: "easyocr" | "tesseract" | ... (default: "easyocr")
- `table_mode`: "fast" | "accurate" (default: "accurate")
- `do_table_structure`: boolean (default: true)
- `page_range`: [start, end] (default: all pages)

**Response**:
```json
{
  "document": {
    "md": "# Document Title\n\n## Section 1\n\nContent...",
    "json": {...},  // if requested
    "html": "..."   // if requested
  },
  "status": "success",
  "processing_time": 45.2,
  "timings": {...}
}
```

### UI Playground

Docling Serve provides a web UI for testing:
- **URL**: http://localhost:5001/ui
- **Features**:
  - Upload PDF files
  - Configure conversion options
  - View markdown/JSON output
  - Download results

### API Documentation

- **Swagger UI**: http://localhost:5001/docs
- **Scalar Docs**: http://localhost:5001/scalar
- **OpenAPI JSON**: http://localhost:5001/openapi.json

## Performance Comparison

### First Upload (Cold Start)

| Metric | Embedded Docling | Docling Serve |
|--------|------------------|---------------|
| Model download | 5-10 minutes | 0 sec (pre-cached) |
| PDF processing | 1-2 minutes | 30-60 sec |
| **Total** | **7-12 minutes** | **30-60 seconds** |

### Subsequent Uploads

| Metric | Embedded Docling | Docling Serve |
|--------|------------------|---------------|
| PDF processing | 1-2 minutes | 30-60 sec |
| Parallelization | Limited (thread pool) | Scalable (multiple instances) |

### Resource Usage

**Embedded Docling**:
- Memory: 500MB-1GB per request
- CPU: High during processing
- Risk: OOM kills, crashes

**Docling Serve**:
- Memory: Isolated in separate container
- CPU: Isolated, configurable limits
- Risk: Minimal (container restart on failure)

## Troubleshooting

### Connection Errors

**Error**: `Failed to connect to Docling Serve`

**Causes**:
1. Docling Serve not running
2. Wrong URL (use `http://docling-serve:5001` not `localhost:5001`)
3. Network issues between containers

**Solutions**:
```bash
# Check if Docling Serve is up
docker-compose ps docling-serve

# Check health
docker-compose exec backend curl http://docling-serve:5001/health

# View logs
docker-compose logs docling-serve
```

### 422 Validation Errors

**Error**: `Docling Serve API error: 422`

**Cause**: Invalid request parameters

**Check**:
- `files` parameter (not `file`)
- `to_formats` as array: `["md"]` (not string)
- Valid format names: `md`, `json`, `html`, `text`, `doctags`

### Processing Timeouts

**Error**: `Server disconnected without sending a response`

**Causes**:
1. Large PDF (100+ pages)
2. Default timeout too short
3. OCR on scanned documents

**Solutions**:
```python
# Increase timeout in pdf_parser_serve.py
async with httpx.AsyncClient(timeout=600.0) as client:  # 10 minutes

# Or disable OCR for faster processing
data={
    "to_formats": ["md"],
    "do_ocr": False,  # Skip OCR
}
```

### Memory Issues

**Error**: Container OOM killed

**Solutions**:
```yaml
# docker-compose.yml
services:
  docling-serve:
    deploy:
      resources:
        limits:
          memory: 8G  # Increase memory limit
```

## Scaling for Production

### Multiple Docling Serve Instances

```yaml
services:
  docling-serve-1:
    image: quay.io/docling-project/docling-serve:latest
    ports:
      - "5001:5001"

  docling-serve-2:
    image: quay.io/docling-project/docling-serve:latest
    ports:
      - "5002:5001"

  docling-serve-3:
    image: quay.io/docling-project/docling-serve:latest
    ports:
      - "5003:5001"
```

### Load Balancing

Use a load balancer (nginx, HAProxy, or Kubernetes service) to distribute requests across instances.

### GPU Acceleration

Use CUDA-enabled Docling Serve image for faster processing:

```yaml
services:
  docling-serve:
    image: quay.io/docling-project/docling-serve:cuda12.8
    runtime: nvidia
    environment:
      NVIDIA_VISIBLE_DEVICES: all
```

## Migration from Embedded Docling

### Files Changed

1. ✅ `docker-compose.yml` - Added docling-serve service
2. ✅ `backend/requirements.txt` - Replaced `docling` with `httpx`
3. ✅ `backend/app/core/config.py` - Added `docling_serve_url` setting
4. ✅ `backend/app/services/pdf_parser_serve.py` - New API-based parser
5. ✅ `backend/app/services/document_processor.py` - Updated imports
6. ✅ `backend/Dockerfile` - Removed docling warm-up step

### Files Removed

- `backend/app/services/pdf_parser.py` - Old embedded Docling parser
- `backend/warm_docling.py` - Model pre-warming script (no longer needed)

### Backward Compatibility

None - this is a breaking change. All existing uploads must use the new architecture.

## Benefits Summary

✅ **Reliability** - No more crashes from model downloads or OOM
✅ **Speed** - Instant startup, faster first upload (30s vs 7-12min)
✅ **Maintainability** - Easier to update Docling (just pull new image)
✅ **Scalability** - Can scale Docling Serve independently
✅ **Observability** - Separate logs for PDF processing
✅ **Development** - Backend restarts don't reload models
✅ **Testing** - Can mock Docling Serve API easily

## Next Steps

1. ✅ Integrate Docling Serve into docker-compose
2. ✅ Refactor PDF parser to use HTTP API
3. ✅ Test with sample PDFs
4. ⏳ Add retry logic for transient failures
5. ⏳ Implement webhook notifications for completion
6. ⏳ Add metrics/monitoring for Docling Serve
7. ⏳ Production deployment with GPU acceleration
