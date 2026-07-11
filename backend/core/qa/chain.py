from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core.retrieval.hybrid import hybrid_search
from backend.core.retrieval.reranker import rerank
from backend.core.qa.history import format_history
from backend.db.faiss_store import load_store


_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = Ollama(model="qwen2.5:3b")
    return _llm


def build_context(chunks: list) -> str:
    context_parts = []
    for i, result in enumerate(chunks):
        chunk = result["chunk"]
        source = chunk["metadata"].get("source", "unknown")
        page = chunk["metadata"].get("page", 0)
        text = chunk.get("parent_text", chunk.get("child_text", ""))
        context_parts.append(f"[{i+1}] من {source} صفحة {page}:\n{text}")
    return "\n\n".join(context_parts)


def build_citations(chunks: list) -> list:
    citations = []
    seen = set()
    for i, result in enumerate(chunks):
        chunk = result["chunk"]
        source = chunk["metadata"].get("source", "unknown")
        page = chunk["metadata"].get("page", 0)
        key = f"{source}-{page}"
        if key not in seen:
            seen.add(key)
            citations.append({
                "index": i + 1,
                "source": source,
                "page": page
            })
    return citations

def compute_confidence(chunks: list) -> float:
    if not chunks:
        return 0.0
    top_score = chunks[0].get("rerank_score", 0.0)
    if top_score > 0.8:
        return 1.0
    elif top_score > 0.5:
        return 0.7
    elif top_score > 0.2:
        return 0.4
    return 0.1


PROMPT = PromptTemplate.from_template("""
You are a helpful assistant. Answer ONLY in Arabic language. Never use Chinese, English or any other language.
If you cannot find the answer in the context, say: لا تتوفر هذه المعلومات في المستندات

Previous conversation:
{history}

Context:
{context}

Question: {question}

Answer in Arabic only:
""")


def answer_question(user_id: str, question: str, history: list = []) -> dict:
    index, chunks = load_store(user_id)
    if index is None or not chunks:
        return {
            "answer": "لم يتم رفع أي مستندات بعد.",
            "citations": [],
            "confidence": 0.0
        }

    hybrid_results = hybrid_search(user_id, question, k=10)
    reranked_results = rerank(question, hybrid_results, top_k=5)

    context = build_context(reranked_results)
    citations = build_citations(reranked_results)
    confidence = compute_confidence(reranked_results)
    formatted_history = format_history(history)

    llm = get_llm()
    chain = PROMPT | llm | StrOutputParser()

    answer = chain.invoke({
        "history": formatted_history,
        "context": context,
        "question": question
    })

    return {
        "answer": answer,
        "citations": citations,
        "confidence": confidence
    }