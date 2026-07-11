import os
from langfuse import Langfuse
from datetime import datetime


_langfuse = None


def get_langfuse():
    global _langfuse
    if _langfuse is None:
        _langfuse = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
    return _langfuse


def trace_query(
    user_id: str,
    question: str,
    answer: str,
    citations: list,
    confidence: float,
    latency_ms: float,
    num_chunks: int
):
    try:
        lf = get_langfuse()

        trace = lf.trace(
            name="rag-query",
            user_id=user_id,
            input={"question": question},
            output={"answer": answer},
            tags=["rag", "query"],
            metadata={
                "confidence": confidence,
                "num_chunks": num_chunks,
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        trace.span(
            name="retrieval",
            input={"question": question},
            output={"num_chunks": num_chunks},
            metadata={"latency_ms": latency_ms}
        )

        trace.span(
            name="generation",
            input={"question": question},
            output={"answer": answer},
            metadata={"confidence": confidence}
        )

        lf.flush()

    except Exception as e:
        print(f"Langfuse error: {e}")


def trace_ingestion(user_id: str, filename: str, num_chunks: int, latency_ms: float):
    try:
        lf = get_langfuse()

        lf.trace(
            name="document-ingestion",
            user_id=user_id,
            input={"filename": filename},
            output={"num_chunks": num_chunks},
            tags=["ingestion"],
            metadata={
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        lf.flush()

    except Exception as e:
        print(f"Langfuse error: {e}")