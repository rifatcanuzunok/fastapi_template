from typing import Any, List, Optional

import redis


class RedisDAO:
    def __init__(self, host: str, port: int, exp: int = None, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db)
        self.exp = exp

    def set(self, key: str, value: Any) -> bool:
        return self.client.set(key, value, self.exp)

    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        return value.decode() if value is not None else None

    def delete(self, key: str) -> bool:
        return self.client.delete(key)

    def keys(self, pattern: str) -> List[str]:
        return self.client.keys(pattern)

    def setnx(self, key: str, value: Any) -> bool:
        return self.client.setnx(key, value)

    def expire(self, key: str, seconds: int) -> bool:
        return self.client.expire(key, seconds)
