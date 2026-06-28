import time
from functools import lru_cache
from typing import Dict, Any, Tuple
import hashlib
import json

class SimpleCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Tuple[float, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl

    def _hash_key(self, key_data: Any) -> str:
        s = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def get(self, key_data: Any) -> Any:
        key = self._hash_key(key_data)
        if key in self.cache:
            timestamp, data = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key_data: Any, value: Any):
        if len(self.cache) >= self.max_size:
            # Simple eviction: clear cache completely or pop oldest. We'll just clear for simplicity
            self.cache.clear()
        key = self._hash_key(key_data)
        self.cache[key] = (time.time(), value)

# Singleton cache instance
cache_store = SimpleCache()
