import asyncio
from enum import Enum, auto
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


class AnonIdBehavior(Enum):
    RETURN_EXPIRED = auto()
    RETURN_NONE = auto()
    GENERATE_NEW = auto()


class AnonIdentity:
    def __init__(
        self,
        user_id: int,
        channel_id: int,
        timeout: Optional[float] = None,
    ):
        self._created = time()
        self._last_used = self._created
        self._timeout = (timeout or get_settings().anon.timeout_mins) * 60
        self._hook: disnake.Webhook | None = None
        self._id = f"{user_id}|{channel_id}"
        self.new_id()

    def _generate_id(
        self,
        seed: Optional[str | int] = None,
        timestamp: Optional[float] = None,
        id_length: Optional[int] = None,
    ) -> str:
        seed = seed or self._id
        timestamp = timestamp or time()
        id_length = id_length or get_settings().anon.hash_length

        buf = f"{seed}|{timestamp}"
        return hashlib.md5(buf.encode()).hexdigest()[:id_length]

    def new_id(self) -> str:
        self._id = self._generate_id()
        self._created = time()
        self._last_used = self._created
        self._icon = blockies.create(self._id, size=8, scale=16)
        if self._hook:
            asyncio.create_task(self._hook.delete())
        self._hook = None
        return self._id

    @property
    def expired(self) -> bool:
        return time() > (self._last_used + self._timeout)

    def peek_id(self, expired_behavior: AnonIdBehavior = AnonIdBehavior.RETURN_NONE):
        if self.expired:
            match expired_behavior:
                case AnonIdBehavior.RETURN_EXPIRED:
                    pass
                case AnonIdBehavior.RETURN_NONE:
                    return None
                case AnonIdBehavior.GENERATE_NEW:
                    return self.new_id
        return self._id

    def use_id(self) -> str:
        id: str = self.peek_id(AnonIdBehavior.GENERATE_NEW)
        self._last_used = time()
        return id

    @property
    def id(self) -> str:
        return self.use_id()

    @property
    def icon(self) -> bytes:
        self.use_id()
        return self._icon

    @property
    def hook(self) -> disnake.Webhook | None:
        self.use_id()
        return self._hook

    @hook.setter
    def hook(self, hook: disnake.Webhook):
        self._hook = hook


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
    def __delitem__(self, channel_id: int):
        try:
            del self._identities[channel_id]
        except KeyError:
            pass

    def clear(self):
        self._identities = {}


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

    @resolves_user
    def __delitem__(self, user_id: int):
        try:
            del self._users[user_id]
        except KeyError:
            pass

    def clear(self):
        self._users = {}
