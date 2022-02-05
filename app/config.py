import functools
from typing import List, Optional
from pydantic import BaseSettings, BaseModel


class Environment(BaseSettings):
    config_file: str = "./machineelf.json"

    class Config:
        env_file = ".env"


class Config(BaseModel):
    class BotConfig(BaseModel):
        token: str
        owner_id: Optional[int]
        guilds: Optional[List[int]]

    bot: BotConfig


@functools.lru_cache()
def get_settings():
    return Config.parse_file(Environment().config_file)
