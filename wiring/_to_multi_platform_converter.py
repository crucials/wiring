from abc import ABC, abstractmethod

from wiring.multi_platform_resources import (MultiPlatformChatGroup,
                                               MultiPlatformMessage,
                                               MultiPlatformChat,
                                               MultiPlatformUser)


class ToMultiPlatformConverter(ABC):
    @abstractmethod
    def convert_to_multi_platform_message(self, message) -> MultiPlatformMessage:
        pass

    @abstractmethod
    def convert_to_multi_platform_user(self, user) -> MultiPlatformUser:
        pass

    @abstractmethod
    def convert_to_multi_platform_chat_group(self, chat_group) -> MultiPlatformChatGroup:
        pass

    @abstractmethod
    def convert_to_multi_platform_chat(self, chat) -> MultiPlatformChat:
        pass
