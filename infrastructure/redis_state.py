# infrastructure/redis_state.py
# CYBER TRADE WIN v3.0 — Redis real com fallback mock

import json
import logging
import os
from typing import Optional

logger = logging.getLogger("redis_state")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

_redis_client = None
_usar_mock = False


def _get_redis():
    global _redis_client, _usar_mock
    if _usar_mock:
        return None
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            _redis_client.ping()
            logger.info(f"Redis conectado: {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis não disponível: {e}. Usando mock.")
            _usar_mock = True
            _redis_client = None
    return _redis_client


class RedisState:
    def __init__(self, host=None, port=None, password=None):
        self.host = host or REDIS_HOST
        self.port = port or REDIS_PORT
        self.password = password
        self._mock_data = {} if _usar_mock else None

    def get(self, key: str) -> Optional[str]:
        client = _get_redis()
        if client:
            try:
                return client.get(key)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        if self._mock_data is not None:
            return self._mock_data.get(key)
        return None

    def set(self, key: str, value: str, ex: int = None):
        client = _get_redis()
        if client:
            try:
                if ex:
                    client.set(key, value, ex=ex)
                else:
                    client.set(key, value)
                return
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        if self._mock_data is not None:
            self._mock_data[key] = value

    def delete(self, key: str):
        client = _get_redis()
        if client:
            try:
                client.delete(key)
                return
            except Exception:
                pass
        if self._mock_data and key in self._mock_data:
            del self._mock_data[key]

    def incr(self, key: str):
        client = _get_redis()
        if client:
            try:
                client.incr(key)
                return
            except Exception:
                pass
        if self._mock_data:
            current = int(self._mock_data.get(key, 0))
            self._mock_data[key] = str(current + 1)

    def get_capital(self) -> Optional[float]:
        v = self.get("capital_atual")
        if v:
            try:
                return float(v)
            except:
                pass
        return 1000.0

    def set_capital(self, value: float):
        self.set("capital_atual", str(value))