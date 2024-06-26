import logging
from typing import Optional
from telegram import Chat, Message, User, ChatFullInfo

from wiring._to_multi_platform_converter import ToMultiPlatformConverter
from wiring.multi_platform_resources import (MultiPlatformChatGroup, MultiPlatformMessage,
                                      MultiPlatformChat, MultiPlatformUser)


class TelegramEntitiesConverter(ToMultiPlatformConverter):
    def convert_to_multi_platform_chat_group(self, chat_group: Chat):
        logger = logging.getLogger('telegram')
        logger.warning('chat group is the same entity as the chat for telegram')

        return MultiPlatformChatGroup('telegram',
                                      chat_group.id,
                                      chat_group.title or chat_group.full_name)

    def convert_to_multi_platform_chat(self, chat: Chat | ChatFullInfo):
        return MultiPlatformChat('telegram',
                                 chat.id,
                                 chat.title or chat.full_name)

    def convert_to_multi_platform_user(self, user: User,
                                       from_chat: Optional[MultiPlatformChatGroup] = None):
        return MultiPlatformUser('telegram', user.username or user.full_name, from_chat)

    def convert_to_multi_platform_message(
        self, message: Message
    ):
        chat = self.convert_to_multi_platform_chat_group(message.chat)

        author_user = (self.convert_to_multi_platform_user(message.from_user, chat)
                       if message.from_user is not None else None)

        return MultiPlatformMessage(
            'telegram',
            message.id,
            chat,
            self.convert_to_multi_platform_chat(message.chat),
            message.text,
            author_user
        )


telegram_entities_converter = TelegramEntitiesConverter()
