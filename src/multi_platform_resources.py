from dataclasses import dataclass
from typing import Any, Literal


Platform = Literal['discord', 'telegram']


MultiPlatformValue = dict[Platform, Any]


MultiPlatformId = str | int


@dataclass
class MultiPlatformMessage():
    platform: Platform
    id: MultiPlatformId
    chat_id: MultiPlatformId
    content: str
