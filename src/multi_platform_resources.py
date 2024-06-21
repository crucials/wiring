from dataclasses import dataclass
from typing import Any, Literal, Optional, TypedDict


Platform = Literal['discord', 'telegram']


MultiPlatformValue = dict[Platform, Any]


MultiPlatformId = str | int


class PlatformSpecificValue(TypedDict):
    platform: Platform
    value: Any


@dataclass
class MultiPlatformChat:
    """
    telegram chat, discord server or other platform chat where message was sent
    """
    platform: Platform
    id: MultiPlatformId
    name: Optional[str]


@dataclass
class MultiPlatformSubChat:
    """
    represents a chat on platforms where there
    can be multiple chats that are grouped in some entity like discord server
    or discord private messages
    """
    platform: Platform
    id: MultiPlatformId
    name: Optional[str]


@dataclass
class MultiPlatformUser:
    platform: Platform
    username: str
    from_chat: Optional[MultiPlatformChat]


@dataclass
class MultiPlatformMessage():
    platform: Platform
    id: MultiPlatformId
    chat: Optional[MultiPlatformChat]
    sub_chat: Optional[MultiPlatformSubChat]
    text: Optional[str]
    author_user: Optional[MultiPlatformUser]
