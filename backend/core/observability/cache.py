import hashlib
import json
import os
import time


CACHE_DIR = "cache"
CACHE_TTL = 60 * 60 * 24


def get_cache_key(user_id: str, question: str) -> str:
    content = f"{user_id}:{question.strip().lower()}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cache_path(cache_key: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{cache_key}.json")


def get_cached_response(user_id: str, question: str):
    cache_key = get_cache_key(user_id, question)
    cache_path = get_cache_path(cache_key)

    if not os.path.exists(cache_path):
        return None

    with open(cache_path, "r", encoding="utf-8") as f:
        cached = json.load(f)

    if time.time() - cached["timestamp"] > CACHE_TTL:
        os.remove(cache_path)
        return None

    return cached["response"]


def set_cached_response(user_id: str, question: str, response: dict):
    cache_key = get_cache_key(user_id, question)
    cache_path = get_cache_path(cache_key)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.time(),
            "response": response
        }, f, ensure_ascii=False)


def clear_user_cache(user_id: str):
    if not os.path.exists(CACHE_DIR):
        return
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CACHE_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    pass
                os.remove(filepath)
            except:
                pass