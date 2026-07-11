import json
import os
import pickle
from rank_bm25 import BM25Okapi
from backend.core.ingest.cleaner import clean_text


STORE_DIR = "vectorstore"


def tokenize(text: str) -> list:
    cleaned, _ = clean_text(text)
    return cleaned.split()


def build_bm25_index(user_id: str, chunks: list):
    tokenized_chunks = [tokenize(chunk["child_text"]) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    path = os.path.join(STORE_DIR, user_id, "bm25.pkl")
    with open(path, "wb") as f:
        pickle.dump(bm25, f)
    return bm25


def load_bm25_index(user_id: str):
    path = os.path.join(STORE_DIR, user_id, "bm25.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def search_bm25(user_id: str, query: str, k: int = 10) -> list:
    bm25 = load_bm25_index(user_id)
    if bm25 is None:
        return []

    from backend.db.faiss_store import load_store
    _, chunks = load_store(user_id)
    if not chunks:
        return []

    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "chunk": chunks[idx],
                "score": float(scores[idx])
            })

    return results