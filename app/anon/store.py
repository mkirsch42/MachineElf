import asyncio
import functools
import hashlib
from time import time
from typing import Callable, Concatenate, Dict, Optional, ParamSpec, TypeVar
import disnake
import blockies

from app.config import get_settings

P = ParamSpec("P")
R = TypeVar("R")
Self = TypeVar("Self")


class AnonIdentity:
    def __init__(self, user_id: int, channel_id: int):
        self._last_used = time()

        id_seed = f"{user_id}|{channel_id}|{time()}"
        id_length = get_settings().anon.hash_length
        self._id = hashlib.md5(id_seed.encode()).hexdigest()[:id_length]

        self._icon = blockies.create(self._id, size=8, scale=16)

        self._hook: disnake.Webhook | None = None
        self._hook_timeout_task: asyncio.Task | None = None

    def touch(self):
        self._last_used = time()

    @property
    def timeout(self) -> float:
        return self._last_used + (get_settings().anon.timeout_mins * 60)

    @property
    def expired(self) -> bool:
        return time() > self.timeout

    @property
    def id(self) -> str:
        return self._id

    @property
    def icon(self) -> bytes:
        return self._icon

    @property
    def hook(self) -> disnake.Webhook | None:
        return self._hook

    async def _hook_timeout(self):
        while not self.expired:
            await asyncio.sleep(self.timeout - time())
        if self._hook:
            await self._hook.delete(reason="timeout")
            self._hook = None

    @hook.setter
    def hook(self, hook: disnake.Webhook):
        if self._hook:
            raise AttributeError("Cannot reassign AnonIdentity.hook")
        self._hook = hook
        self._hook_timeout_task = asyncio.create_task(self._hook_timeout())

    async def cleanup(self, delete_reason: str = "AnonIdentity.cleaup()"):
        if self._hook_timeout_task and not self._hook_timeout_task.done():
            self._hook_timeout_task.cancel()
            try:
                await self._hook_timeout_task
            except asyncio.CancelledError:
                pass
        if self._hook:
            await self._hook.delete(reason=delete_reason)


class AnonUserRecord:
    def __init__(self, user_id: int):
        self._user_id = user_id
        self._identities: Dict[int, AnonIdentity] = {}

    def resolves_channel(
        func: Callable[Concatenate[Self, int, P], R]
    ) -> Callable[Concatenate[Self, disnake.TextChannel | disnake.Thread | int, P], R]:
        @functools.wraps(func)
        def wrap(
            self: Self,
            channel: disnake.TextChannel | disnake.Thread | int,
            *args,
            **kwargs,
        ):
            if not isinstance(channel, int):
                channel = channel.id
            return func(self, channel, *args, **kwargs)

        return wrap

    @resolves_channel
    def __contains__(self, channel_id: int) -> bool:
        return channel_id in self._identities

    @resolves_channel
    def __getitem__(self, channel_id: int) -> AnonIdentity:
        rec = self._identities.get(channel_id)
        if not rec:
            rec = AnonIdentity(self._user_id, channel_id)
            self._identities[channel_id] = rec
        return rec

    @resolves_channel
    def delete(
        self, channel_id: int, delete_reason: Optional[str] = None
    ) -> asyncio.Task:
        anon = self._identities.pop(channel_id)
        return asyncio.create_task(anon.cleanup(delete_reason=delete_reason))


class AnonStore:
    def __init__(self):
        self._users: Dict[int, AnonUserRecord] = {}

    def resolves_user(
        func: Callable[Concatenate[Self, int, P], R]
    ) -> Callable[Concatenate[Self, disnake.User | disnake.Member | int, P], R]:
        @functools.wraps(func)
        def wrap(
            self: Self,
            user: disnake.User | disnake.Member | int,
            *args,
            **kwargs,
        ):
            if not isinstance(user, int):
                user = user.id
            return func(self, user, *args, **kwargs)

        return wrap

    @resolves_user
    def __contains__(self, user_id: int) -> bool:
        return user_id in self._users

    @resolves_user
    def __getitem__(self, user_id: int) -> AnonUserRecord:
        rec = self._users.get(user_id)
        if not rec:
            rec = AnonUserRecord(user_id)
            self._users[user_id] = rec
        return rec

    def clear(self):
        self._users = {}
