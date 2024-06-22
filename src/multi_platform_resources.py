from dataclasses import dataclass
from typing import Any, Literal, Optional, TypedDict


Platform = Literal['discord', 'telegram']


MultiPlatformValue = dict[Platform, Any]


MultiPlatformId = str | int


class PlatformSpecificValue(TypedDict):
    platform: Platform
    value: Any


@dataclass
class MultiPlatformChatGroup:
    """
    represents a group of chats like discord server or discord private messages
    """
    platform: Platform
    id: MultiPlatformId
    name: Optional[str]


@dataclass
class MultiPlatformChat:
    """
    telegram chat, discord channel or other platform chat where message was sent
    """
    platform: Platform
    id: MultiPlatformId
    name: Optional[str]


@dataclass
class MultiPlatformUser:
    platform: Platform
    username: str
    from_chat_group: Optional[MultiPlatformChatGroup]


@dataclass
class MultiPlatformMessage():
    platform: Platform
    id: MultiPlatformId
    chat_group: Optional[MultiPlatformChatGroup]
    chat: Optional[MultiPlatformChat]
    text: Optional[str]
    author_user: Optional[MultiPlatformUser]
