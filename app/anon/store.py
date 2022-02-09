import asyncio
import hashlib
from time import time
from typing import (
    Awaitable,
    Optional,
    Sequence,
    Tuple,
)

import blockies
import aioredis
import base64

from app.config import get_settings


class AnonStore:
    def __init__(
        self,
        url: Optional[str] = None,
        prefix: Optional[str] = None,
        *,
        id_length: Optional[int] = None,
        timeout: Optional[int] = None,
        resolution: Optional[int] = None,
    ):
        self._redis = aioredis.from_url(
            url or get_settings().db.redis, decode_responses=True
        )
        self._prefix = prefix or get_settings().anon.redis_prefix
        self._id_length = id_length or get_settings().anon.hash_length
        self._timeout = timeout or int(get_settings().anon.timeout_mins * 60)
        self._resolution = resolution or get_settings().anon.icon_resolution

    async def delete_id(self, path: Sequence[str | int]):
        key = ".".join(str(v) for v in path)

        await asyncio.gather(
            self._redis.delete(f"{self._prefix}{key}"),
            self._redis.delete(f"{self._prefix}{key}.icon"),
        )

    async def create_id(self, path: Sequence[str | int]) -> Tuple[str, bytes]:
        key = ".".join(str(v) for v in path)

        seed = f"{key}{time()}".encode()
        anon_id = hashlib.md5(seed).hexdigest()[: self._id_length]
        icon = blockies.create(
            anon_id, size=self._resolution, scale=int(128 / self._resolution)
        )

        await asyncio.gather(
            self._redis.set(f"{self._prefix}{key}", anon_id, self._timeout),
            self._redis.set(
                f"{self._prefix}{key}.icon", base64.encodebytes(icon), self._timeout
            ),
            self._redis.set(f"{self._prefix}${anon_id}", key),
        )
        return anon_id, icon

    async def get(self, path: Sequence[str | int]) -> Tuple[str, bytes, bool]:
        key = ".".join(str(v) for v in path)

        id_key = f"{self._prefix}{key}"
        icon_key = f"{id_key}.icon"

        anon_id: str | None
        icon: str | None
        anon_id, icon = await asyncio.gather(
            self._redis.get(id_key),
            self._redis.get(icon_key),
        )

        if anon_id is None or icon is None:
            return *(await self.create_id(path)), True

        await asyncio.gather(
            self._redis.expire(id_key, self._timeout),
            self._redis.expire(icon_key, self._timeout),
        )
        return anon_id, base64.decodebytes(icon.encode()), False

    def __getitem__(
        self, path: Sequence[str | int]
    ) -> Awaitable[Tuple[str, bytes, bool]]:
        return self.get(path)
