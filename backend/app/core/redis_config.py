# app/core/redis_config.py
import redis
import os
import logging

logger = logging.getLogger("uvicorn.error")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("⚡ Redis Cache Layer connected successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize Redis: {e}")
    redis_client = None

def get_cached_string(key: str) -> str | None:
    if not redis_client:
        return None
    try:
        raw_val = redis_client.get(key)
        if raw_val is None:
            return None
        # FIXED: Explicit guard evaluation to decode bytes safely if static checker panics
        if isinstance(raw_val, bytes):
            return raw_val.decode("utf-8")
        return str(raw_val)
    except Exception:
        return None

def set_cached_string(key: str, value: str, expire_seconds: int = 3600) -> bool:
    if not redis_client:
        return False
    try:
        redis_client.setex(key, expire_seconds, value)
        return True
    except Exception:
        return False