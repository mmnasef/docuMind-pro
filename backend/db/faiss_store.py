import os
import json
import faiss
import numpy as np


STORE_DIR = "vectorstore"


def get_user_store_path(user_id: str) -> str:
    path = os.path.join(STORE_DIR, user_id)
    os.makedirs(path, exist_ok=True)
    return path


def save_store(user_id: str, index: faiss.Index, chunks: list):
    path = get_user_store_path(user_id)
    faiss.write_index(index, os.path.join(path, "index.faiss"))
    with open(os.path.join(path, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)


def load_store(user_id: str):
    path = get_user_store_path(user_id)
    index_path = os.path.join(path, "index.faiss")
    chunks_path = os.path.join(path, "chunks.json")

    if not os.path.exists(index_path):
        return None, []

    index = faiss.read_index(index_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return index, chunks


def add_chunks_to_store(user_id: str, embeddings: list, chunks: list):
    vectors = np.array(embeddings, dtype=np.float32)
    faiss.normalize_L2(vectors)

    index, existing_chunks = load_store(user_id)

    if index is None:
        dimension = vectors.shape[1]
        index = faiss.IndexFlatIP(dimension)

    index.add(vectors)
    existing_chunks.extend(chunks)
    save_store(user_id, index, existing_chunks)


def search_store(user_id: str, query_embedding: list, k: int = 10):
    index, chunks = load_store(user_id)

    if index is None or len(chunks) == 0:
        return []

    query_vector = np.array([query_embedding], dtype=np.float32)
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:
            chunk = chunks[idx]
            results.append({
                "chunk": chunk,
                "score": float(score)
            })

    return results
    