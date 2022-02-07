import functools
from typing import Any, Dict, List, Optional
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


class LoggingConfig(BaseModel):
    levels: Dict[str, str | int] = {}
    setup: Dict[str, Any] = {"level": "INFO"}


class Config(BaseModel):
    bot: BotConfig
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    anon: AnonConfig = Field(default_factory=AnonConfig)


@functools.lru_cache()
def get_settings():
    return Config.parse_file(Environment().config_file)
