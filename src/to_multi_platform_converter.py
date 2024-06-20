from abc import ABC, abstractmethod

from multi_platform_resources import (MultiPlatformChat, MultiPlatformMessage,
                                      MultiPlatformSubChat, MultiPlatformUser)


class ToMultiPlatformConverter(ABC):
    @abstractmethod
    def convert_to_multi_platform_message(self, message) -> MultiPlatformMessage:
        pass

    @abstractmethod
    def convert_to_multi_platform_user(self, user) -> MultiPlatformUser:
        pass

    @abstractmethod
    def convert_to_multi_platform_chat(self, chat) -> MultiPlatformChat:
        pass

    @abstractmethod
    def convert_to_multi_platform_sub_chat(self,
                                           sub_chat) -> MultiPlatformSubChat:
        pass
