# Event-Driven Document Management System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-AsyncIO-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Architecture-Microservices-orange.svg" alt="Architecture">
  <img src="https://img.shields.io/badge/CDC-Debezium-red.svg" alt="CDC">
</p>

##  Overview

A microservices architecture showing event-driven document management with Change Data Capture (CDC), real-time updates, and full-text search capabilities. Built entirely with **async Python** for maximum throughput and minimal resource consumption.

## Testing with Curl

You can test the flow (Document Creation -> Signature -> Status Update) using the following commands.

### 1. Create a Document
**Service:** Document Service (Port 8005)

**Option A: Inline JSON**
```bash
curl -X POST http://localhost:8005/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sales Agreement Q4 2025",
    "content": "This agreement outlines the terms...",
    "created_by": "ebemad@company.com"
  }' | jq '.'
```


**Option B: Using a JSON File (S3 Upload)**
```bash
curl -X POST http://localhost:8005/documents \
  -H "Content-Type: application/json" \
  -d @sample_doc.json | jq '.'
```
*Response:* Note the `id` field from the response (e.g., `06946681-6080-71f1-8000-e0ba48255d59`).

### 2. Sign the Document
**Service:** Signature Service (Port 8002)
**Trigger:** This will trigger a gRPC call to update the document status to `signed`.

Replace `YOUR_DOCUMENT_ID` with the ID from Step 1.

```bash
curl -X POST http://localhost:8002/signatures \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "YOUR_DOCUMENT_ID",
    "signer_email": "ebemad@client.com",
    "signer_name": "Ebrahim Emad",
    "signature_data": "base64encoded_signature_image_data_here",
    "document_status":"pending"
  }' | jq '.'
```

### 3. Verify Document Status
**Service:** Document Service (Port 8005)

Check that the document status has been updated to `signed`.

```bash
curl http://localhost:8005/documents/YOUR_DOCUMENT_ID | jq '.'
```
