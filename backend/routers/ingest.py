import os
import time
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from backend.auth.jwt import get_current_user
from backend.core.ingest.loader import load_file
from backend.core.ingest.chunker import chunk_documents
from backend.core.retrieval.embeddings import embed_chunks
from backend.db.faiss_store import add_chunks_to_store
from backend.core.retrieval.bm25 import build_bm25_index
from backend.db.faiss_store import load_store
from backend.core.observability.langfuse_client import trace_ingestion
from backend.core.observability.cache import clear_user_cache

router = APIRouter(prefix="/ingest", tags=["ingest"])

UPLOAD_DIR = "uploads"
jobs = {}


def process_document(user_id: str, filepath: str, job_id: str):
    try:
        jobs[job_id] = {"status": "processing", "progress": "loading file"}
        start_time = time.time()
        documents = load_file(filepath)
        jobs[job_id]["progress"] = "chunking"
        chunks = chunk_documents(documents)
        jobs[job_id]["progress"] = "embedding"
        embeddings = embed_chunks(chunks)
        jobs[job_id]["progress"] = "saving"
        add_chunks_to_store(user_id, embeddings, chunks)
        _, all_chunks = load_store(user_id)
        build_bm25_index(user_id, all_chunks)
        clear_user_cache(user_id)
        latency_ms = (time.time() - start_time) * 1000
        trace_ingestion(user_id=user_id, filename=os.path.basename(filepath), num_chunks=len(chunks), latency_ms=latency_ms)
        jobs[job_id] = {"status": "completed", "num_chunks": len(chunks), "latency_ms": latency_ms}
    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}


@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    print(f"USER ID: {user_id}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    job_id = f"{user_id}_{int(time.time())}"
    jobs[job_id] = {"status": "queued"}
    background_tasks.add_task(process_document, user_id, filepath, job_id)
    return {"job_id": job_id, "message": "File uploaded, processing started"}


@router.get("/status/{job_id}")
def get_job_status(job_id: str, user_id: str = Depends(get_current_user)):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@router.get("/documents")
def list_documents(user_id: str = Depends(get_current_user)):
    _, chunks = load_store(user_id)
    if not chunks:
        return {"documents": []}
    sources = {}
    for chunk in chunks:
        source = chunk["metadata"].get("source", "unknown")
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
    return {"documents": [{"filename": src, "num_chunks": count} for src, count in sources.items()]}