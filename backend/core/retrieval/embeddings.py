from langchain_ollama import OllamaEmbeddings
from typing import List


_embeddings_model = None


def get_embeddings_model():
    global _embeddings_model
    if _embeddings_model is None:
        _embeddings_model = OllamaEmbeddings(model="nomic-embed-text")
    return _embeddings_model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embeddings_model()
    return model.embed_documents(texts)


def embed_query(text: str) -> List[float]:
    model = get_embeddings_model()
    return model.embed_query(text)


def embed_chunks(chunks: List[dict]) -> List[List[float]]:
    texts = [chunk["child_text"] for chunk in chunks]
    return embed_texts(texts)