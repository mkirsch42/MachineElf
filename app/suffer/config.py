from typing import List
from pydantic import BaseModel, Field


class SufferMessages(BaseModel):
    stats_count: str = "{} messages"
    stats_title: str = "Recent Stats"
    stats_range: str = "Last {} days"
    stats_alltime: str = "All Time"
    new_event_options: List[str] = [
        "Somebody tried sourcing substances! Time for **{}** pushups 💪 and minutes of meditation 🧘"
    ]


class SufferConfig(BaseModel):
    messages: SufferMessages = Field(default_factory=SufferMessages)
    ranges: List[int] = [30, 90, 365, -1]
    embed_inline: bool = True
    embed_first_newline: bool = True
    last_n_days: int = 30
