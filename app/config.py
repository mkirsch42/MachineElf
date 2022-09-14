import functools
from typing import Any, Dict, List, Optional
from pydantic import BaseSettings, BaseModel, Field

from app.anon.config import AnonConfig
from app.suffer.config import SufferConfig
from app.collect.config import CollectConfig


class Environment(BaseSettings):
    config_file: str = ".config/machineelf.json"

    class Config:
        env_file = ".env"


class BotConfig(BaseModel):
    token: str
    owner_id: Optional[int]
    guilds: Optional[List[int]]
    admin_roles: List[int] = []


class LoggingConfig(BaseModel):
    levels: Dict[str, str | int] = {}
    setup: Dict[str, Any] = {"level": "INFO"}


class DatabaseConfig(BaseModel):
    redis: str = "redis://localhost"
    sql: str = "postgres://localhost"


class TestConfig(BaseModel):
    guilds: Optional[List[int]] = None


class Config(BaseModel):
    bot: BotConfig
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    test: TestConfig = Field(default_factory=TestConfig)
    anon: AnonConfig = Field(default_factory=AnonConfig)
    suffer: SufferConfig = Field(default_factory=SufferConfig)
    collect: CollectConfig = Field(default_factory=CollectConfig)


@functools.lru_cache()
def get_settings():
    return Config.parse_file(Environment().config_file)
