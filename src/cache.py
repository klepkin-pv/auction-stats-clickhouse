import json
from datetime import timedelta

import redis

from src.config import settings

DEFAULT_TTL = int(timedelta(minutes=5).total_seconds())


def _make_redis_client():
    try:
        client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
        )
        client.ping()
        return client
    except redis.ConnectionError:
        return None


redis_client = _make_redis_client()
_memory_cache: dict[str, tuple[str, int]] = {}


def _memory_get(key: str):
    if key not in _memory_cache:
        return None
    value, _ttl = _memory_cache[key]
    return json.loads(value)


def _memory_set(key: str, value, ttl: int):
    _memory_cache[key] = (json.dumps(value), ttl)


def _memory_delete_pattern(pattern: str):
    keys_to_delete = [k for k in _memory_cache if k.startswith(pattern.replace("*", ""))]
    for k in keys_to_delete:
        del _memory_cache[k]


def cache_key(prefix: str, params: dict) -> str:
    parts = [prefix]
    for key in sorted(params):
        parts.append(f"{key}:{params[key]}")
    return "|".join(parts)


def get_stats(key: str):
    if redis_client:
        raw = redis_client.get(key)
        if raw:
            return json.loads(raw)
        return None
    return _memory_get(key)


def set_stats(key: str, value, ttl: int = DEFAULT_TTL):
    if redis_client:
        redis_client.setex(key, ttl, json.dumps(value))
    else:
        _memory_set(key, value, ttl)


def invalidate_stats():
    if redis_client:
        for key in redis_client.scan_iter(match="stats:*"):
            redis_client.delete(key)
    else:
        _memory_delete_pattern("stats:*")
