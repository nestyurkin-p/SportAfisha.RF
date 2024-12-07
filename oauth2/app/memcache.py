import os
import redis
import hashlib


class MemCache:
    def __init__(self, redis_connection):
        self._r = redis_connection

    def _hash_jwt(self, raw_jwt: str):
        token_hash = hashlib.new("sha256")
        token_hash.update(raw_jwt.encode("utf-8"))
        return token_hash.hexdigest()

    def _key_jwt(self, raw_jwt):
        return f"jwt:{self._hash_jwt(raw_jwt)}"

    def register_jwt(self, raw_jwt: str):
        self._r.set(self._key_jwt(raw_jwt), 0)

    def check_jwt(self, raw_jwt: str) -> bool:
        return self._r.get(self._key_jwt(raw_jwt)) is not None

    def erase_jwt(self, raw_jwt: str):
        self._r.delete(self._key_jwt(raw_jwt))


def get_redis_connection_params():
    REDIS_HOST_FALLBACK = "localhost"
    REDIS_PORT_FALLBACK = 6379
    REDIS_PASSWORD_FALLBACK = "toor"

    REDIS_HOST = os.getenv("REDIS_HOST", REDIS_HOST_FALLBACK)
    REDIS_PORT = os.getenv("REDIS_PORT", REDIS_PORT_FALLBACK)
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", REDIS_PASSWORD_FALLBACK)

    return {
        "host": REDIS_HOST,
        "port": REDIS_PORT,
        "password": REDIS_PASSWORD,
        "decode_responses": True,
    }


_r = redis.Redis(**get_redis_connection_params())

memcache = MemCache(_r)
