from backend.core.retrieval.embeddings import embed_query
from backend.db.faiss_store import search_store
from backend.core.retrieval.bm25 import search_bm25


def reciprocal_rank_fusion(results_list: list, k: int = 60) -> list:
    scores = {}
    chunks_map = {}

    for results in results_list:
        for rank, result in enumerate(results):
            chunk_text = result["chunk"]["child_text"]
            if chunk_text not in scores:
                scores[chunk_text] = 0
                chunks_map[chunk_text] = result["chunk"]
            scores[chunk_text] += 1 / (k + rank + 1)

    sorted_chunks = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [
        {"chunk": chunks_map[text], "score": score}
        for text, score in sorted_chunks
    ]


def hybrid_search(user_id: str, query: str, k: int = 10) -> list:
    query_embedding = embed_query(query)
    semantic_results = search_store(user_id, query_embedding, k=k * 2)
    keyword_results = search_bm25(user_id, query, k=k * 2)

    fused_results = reciprocal_rank_fusion([semantic_results, keyword_results])

    return fused_results[:k]