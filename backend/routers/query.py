import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth.jwt import get_current_user
from backend.core.qa.chain import answer_question
from backend.core.qa.history import add_to_history, trim_history
from backend.core.observability.cache import get_cached_response, set_cached_response
from backend.core.observability.langfuse_client import trace_query


router = APIRouter(prefix="/query", tags=["query"])

user_histories = {}


class QueryRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(
    request: QueryRequest,
    user_id: str = Depends(get_current_user)
):
    cached = get_cached_response(user_id, request.question)
    if cached:
        return {**cached, "cached": True}

    if user_id not in user_histories:
        user_histories[user_id] = []

    history = user_histories[user_id]
    start_time = time.time()

    response = answer_question(
        user_id=user_id,
        question=request.question,
        history=history
    )

    latency_ms = (time.time() - start_time) * 1000

    user_histories[user_id] = trim_history(
        add_to_history(history, request.question, response["answer"])
    )

    set_cached_response(user_id, request.question, response)

    trace_query(
        user_id=user_id,
        question=request.question,
        answer=response["answer"],
        citations=response["citations"],
        confidence=response["confidence"],
        latency_ms=latency_ms,
        num_chunks=len(response["citations"])
    )

    return {**response, "cached": False, "latency_ms": latency_ms}


@router.delete("/history")
def clear_history(user_id: str = Depends(get_current_user)):
    user_histories[user_id] = []
    return {"message": "History cleared"}


@router.get("/history")
def get_history(user_id: str = Depends(get_current_user)):
    history = user_histories.get(user_id, [])
    return {"history": history}