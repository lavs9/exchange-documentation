# Async Document Processing

## Overview

The Exchange API Documentation Manager uses asynchronous background processing for PDF parsing to ensure fast API responses and prevent timeouts.

## Architecture

### Upload Flow

```
Client                  API Server              Background Worker
  |                         |                           |
  |-- POST /upload -------->|                           |
  |                         |                           |
  |                         |- Save file to disk        |
  |                         |- Create DB record         |
  |                         |- Queue background task ---|
  |                         |                           |
  |<-- 202 ACCEPTED --------|                           |
  |    {id, status:         |                           |
  |     "processing"}       |                           |
  |                         |                           |
  |                         |                      [Processing]
  |                         |                      - Parse PDF
  |                         |                      - Extract sections
  |                         |                      - Save to DB
  |                         |                      - Update status
  |                         |                           |
  |-- GET /status --------->|                           |
  |<-- {status: ------------|                           |
  |     "processing"} ------|                           |
  |                         |                           |
  |-- GET /status --------->|                           |
  |<-- {status: ------------|                           |
  |     "completed"} -------|                           |
```

### API Endpoints

#### Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: <PDF file>
title: "NSE CM API"
version: "v6.2"
```

**Response:** `202 ACCEPTED`
```json
{
  "id": "a7760917-04d2-4396-b744-c69fa148bfdd",
  "title": "NSE CM API",
  "version": "v6.2",
  "processing_status": "processing",
  "upload_date": "2025-10-07T16:15:01.612Z",
  "file_path": "/app/uploads/NSE_CM_API_v6.2_20251007_161501.pdf",
  "page_count": null,
  "metadata": null
}
```

#### Check Processing Status
```http
GET /api/documents/{document_id}/status
```

**Response:** `200 OK`
```json
{
  "document_id": "a7760917-04d2-4396-b744-c69fa148bfdd",
  "status": "completed",  // or "processing" or "failed"
  "progress": 100
}
```

#### Get Document Details
```http
GET /api/documents/{document_id}
```

**Response:** `200 OK`
```json
{
  "id": "a7760917-04d2-4396-b744-c69fa148bfdd",
  "title": "NSE CM API",
  "version": "v6.2",
  "processing_status": "completed",
  "page_count": 150,
  "upload_date": "2025-10-07T16:15:01.612Z",
  "file_path": "/app/uploads/NSE_CM_API_v6.2_20251007_161501.pdf"
}
```

## Implementation Details

### Document Processor

The `DocumentProcessor` service has two main methods:

1. **`create_document_record()`** - Synchronous, fast (<1s)
   - Saves uploaded file to disk
   - Creates database record with `status="processing"`
   - Returns immediately

2. **`process_document_async()`** - Asynchronous, slow (1-2min)
   - Runs in FastAPI `BackgroundTasks`
   - Creates its own database session
   - Parses PDF with Docling
   - Extracts sections and hierarchy
   - Updates status to `completed` or `failed`

### Database Sessions

Background tasks create their own database sessions to avoid conflicts:

```python
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async with async_session() as db:
    # Process document
    # Update status
```

### Processing Status States

- **`processing`** - Upload received, PDF parsing in progress
- **`completed`** - PDF parsed successfully, sections extracted
- **`failed`** - Error occurred during processing

## First-Run Behavior

### Model Downloads

Docling downloads ML models on first initialization (~50MB total):
- EasyOCR detection models
- Layout analysis models
- Table structure models

**During first upload:**
- Model download takes 5-10 minutes
- Processing appears slow
- Subsequent uploads are much faster (1-2 minutes)

### Pre-warming in Docker (Recommended)

The Dockerfile includes a `warm_docling.py` script that pre-downloads models during image build:

```dockerfile
RUN python warm_docling.py || true
```

This ensures models are cached in the Docker image, making the first production upload fast.

## Resource Usage

### CPU Usage
- Docling is CPU-intensive (PDF parsing, OCR, layout detection)
- Without GPU: Processing takes 1-2 minutes per document
- With GPU: Processing takes 10-30 seconds per document

### Memory Usage
- Base: ~100MB
- During processing: ~500MB-1GB per document
- Models cached in memory: ~200MB

### Disk Usage
- Models: ~200MB
- Uploaded PDFs: Variable (typically 1-5MB each)

## Testing

Use the provided test script to verify async processing:

```bash
chmod +x test_async_upload.sh
./test_async_upload.sh
```

The script:
1. Uploads a document
2. Polls status every 5 seconds
3. Shows completion time
4. Displays final document details

## Troubleshooting

### Upload succeeds but status check times out

**Cause:** First-time model download in progress

**Solution:** Wait 5-10 minutes for model download to complete, or rebuild Docker image with pre-warming

### Processing stuck at "processing" status

**Check logs:**
```bash
docker-compose logs backend | tail -100
```

Look for:
- Docling progress bars
- Error messages
- Memory warnings

### Container OOM killed

**Increase Docker memory limit:**
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
```

### Multiple uploads queue up

**Expected behavior:** Docling processes one document at a time to avoid memory issues. Subsequent uploads wait in the background task queue.

**To process concurrently:** Increase worker processes or use separate worker containers.

## Production Recommendations

1. **Pre-build Docker image with models** - Uncomment warm_docling.py step
2. **Use GPU if available** - Add CUDA support to Docker image
3. **Monitor background tasks** - Add task queue visibility
4. **Set memory limits** - Prevent OOM kills (recommended: 2-4GB)
5. **Add retry logic** - Retry failed processing automatically
6. **Implement webhooks** - Notify clients when processing completes

## Example Client Code

### JavaScript/TypeScript

```typescript
async function uploadAndWait(file: File, title: string, version: string) {
  // Upload document
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  formData.append('version', version);

  const uploadRes = await fetch('/api/documents/upload', {
    method: 'POST',
    body: formData,
  });

  const doc = await uploadRes.json();
  console.log(`Document ${doc.id} uploaded, status: ${doc.processing_status}`);

  // Poll status
  while (true) {
    await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5s

    const statusRes = await fetch(`/api/documents/${doc.id}/status`);
    const status = await statusRes.json();

    console.log(`Status: ${status.status}`);

    if (status.status === 'completed') {
      console.log('Processing complete!');
      break;
    } else if (status.status === 'failed') {
      console.error('Processing failed');
      break;
    }
  }

  // Get final document
  const finalRes = await fetch(`/api/documents/${doc.id}`);
  return await finalRes.json();
}
```

### Python

```python
import time
import requests

def upload_and_wait(file_path: str, title: str, version: str):
    # Upload document
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'title': title, 'version': version}
        response = requests.post('http://localhost:8000/api/documents/upload',
                                files=files, data=data)

    doc = response.json()
    doc_id = doc['id']
    print(f"Document {doc_id} uploaded, status: {doc['processing_status']}")

    # Poll status
    while True:
        time.sleep(5)  # Wait 5 seconds

        status_response = requests.get(
            f'http://localhost:8000/api/documents/{doc_id}/status'
        )
        status = status_response.json()

        print(f"Status: {status['status']}")

        if status['status'] == 'completed':
            print("Processing complete!")
            break
        elif status['status'] == 'failed':
            print("Processing failed")
            break

    # Get final document
    doc_response = requests.get(f'http://localhost:8000/api/documents/{doc_id}')
    return doc_response.json()
```

## Performance Metrics

Typical processing times (without GPU):

- **File upload**: <100ms
- **Model download (first time only)**: 5-10 minutes
- **PDF parsing (50-page doc)**: 1-2 minutes
- **Section extraction**: 5-10 seconds
- **Database save**: 1-2 seconds

**Total first-upload time**: 7-12 minutes (with model download)
**Total subsequent uploads**: 1-2 minutes
