from typing import Optional
from pydantic import BaseModel, Field


class CollectConfig(BaseModel):
    api_url: Optional[str]
    api_key: Optional[str]
    role_id: Optional[int]
    success_message: str = "Thank you for joining!"
