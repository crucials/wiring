from dataclasses import dataclass
from typing import Any, Literal


Platform = Literal['discord', 'telegram']


MultiPlatformValue = dict[Platform, Any]


@dataclass
class MultiPlatformMessage():
    platform: Platform
    id: Any
    chat_id: Any
    content: str
