# DocuMind Pro

Production-grade Arabic and Multilingual Document Intelligence Platform.
Ask questions in natural language and get source-cited answers from your documents.

## Stack

- FastAPI — REST API backend
- LangChain — LLM orchestration
- FAISS — Vector storage
- BM25 + Semantic Search — Hybrid retrieval
- Cross-encoder — Reranking
- nomic-embed-text — Embeddings via Ollama
- llama3.2:3b — Local LLM via Ollama
- Langfuse — Observability and tracing
- JWT — Authentication

## Features

- Multi-format ingestion: PDF, DOCX, TXT, Web URLs
- Arabic NLP: tashkeel removal, hamza normalization, number normalization
- Parent-child chunking for improved retrieval accuracy
- Hybrid search combining BM25 keyword search and semantic embeddings
- Cross-encoder reranking for precision
- Source citation with document name and page number on every answer
- Confidence scoring per response
- Query caching with 24-hour TTL
- Async background ingestion with job status endpoint
- Multi-tenant: each user's documents are isolated
- JWT authentication

## API Endpoints
POST /auth/register
POST /auth/login
POST /ingest/upload
GET  /ingest/status/{job_id}
GET  /ingest/documents
POST /query/ask
GET  /query/history
DELETE /query/history

## Setup

```bash
git clone https://github.com/mmnasef/docuMind-pro
cd docuMind-pro
pip install -r requirements.txt
cp .env.example .env
ollama pull nomic-embed-text
ollama pull llama3.2:3b
uvicorn backend.main:app --reload
```

## Environment Variables
LANGFUSE_SECRET_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_HOST=
SECRET_KEY=