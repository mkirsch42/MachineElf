import functools
from typing import List, Optional
from pydantic import BaseSettings, BaseModel, Field

from app.anon.config import AnonConfig


class Environment(BaseSettings):
    config_file: str = "./machineelf.json"

    class Config:
        env_file = ".env"


class BotConfig(BaseModel):
    token: str
    owner_id: Optional[int]
    guilds: Optional[List[int]]
    heartbeat_timeout: int = 60


class Config(BaseModel):
    bot: BotConfig
    anon: AnonConfig = Field(default_factory=AnonConfig)


@functools.lru_cache()
def get_settings():
    return Config.parse_file(Environment().config_file)
