from pydantic import BaseModel, Field


class AnonMessages(BaseModel):
    new_id: str = "Generated new id {}. Sending message..."
    sending: str = "Sending message as {}..."
    username: str = "{} (sent with /anon)"


class AnonConfig(BaseModel):
    timeout_mins: float = 1
    hash_length: int = Field(6, ge=4, le=32)
    messages: AnonMessages = Field(default_factory=AnonMessages)
    defer: bool = False
