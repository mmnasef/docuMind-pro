from sentence_transformers import CrossEncoder
from typing import List


_reranker_model = None


def get_reranker():
    global _reranker_model
    if _reranker_model is None:
        _reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker_model


def rerank(query: str, results: List[dict], top_k: int = 5) -> List[dict]:
    if not results:
        return []

    reranker = get_reranker()

    pairs = [(query, result["chunk"]["child_text"]) for result in results]
    scores = reranker.predict(pairs)

    for result, score in zip(results, scores):
        result["rerank_score"] = float(score)

    reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_k]