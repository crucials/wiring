from dataclasses import dataclass
from typing import Any, Literal, Optional


Platform = Literal['discord', 'telegram']


MultiPlatformValue = dict[Platform, Any]


MultiPlatformId = str | int


@dataclass
class MultiPlatformChat:
    platform: Platform
    id: MultiPlatformId
    name: Optional[str]


@dataclass
class MultiPlatformSubChat:
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
    """
    :param chat: id of telegram chat, discord server or other platform chat
    where message was sent

    :param sub_chat: field represents a chat on platforms where there
    can be multiple chats that are grouped in some entity like discord server
    or discord private messages
    """
    platform: Platform
    id: MultiPlatformId
    chat: Optional[MultiPlatformChat]
    sub_chat: Optional[MultiPlatformSubChat]
    text: Optional[str]
    author_user: Optional[MultiPlatformUser]
