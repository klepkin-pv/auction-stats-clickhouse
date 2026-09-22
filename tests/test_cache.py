from unittest.mock import patch

import redis

from src.cache import _make_redis_client


def test_client_returned_when_redis_available():
    with patch("src.cache.redis.Redis") as redis_cls:
        client = _make_redis_client()
    assert client is redis_cls.return_value


def test_fallback_on_connection_error():
    with patch("src.cache.redis.Redis") as redis_cls:
        redis_cls.return_value.ping.side_effect = redis.ConnectionError("refused")
        assert _make_redis_client() is None


def test_fallback_on_protocol_error():
    with patch("src.cache.redis.Redis") as redis_cls:
        redis_cls.return_value.ping.side_effect = redis.ResponseError("unknown command")
        assert _make_redis_client() is None
