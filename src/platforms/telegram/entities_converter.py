import logging
from typing import Optional
from telegram import Chat, Message, User

from to_multi_platform_converter import ToMultiPlatformConverter
from multi_platform_resources import (MultiPlatformChat, MultiPlatformMessage,
                                      MultiPlatformSubChat, MultiPlatformUser)


class TelegramEntitiesConverter(ToMultiPlatformConverter):
    def convert_to_multi_platform_chat(self, chat: Chat):
        return MultiPlatformChat('telegram', chat.id, chat.title or chat.full_name)
    
    def convert_to_multi_platform_sub_chat(self, sub_chat: Chat):
        logger = logging.getLogger('telegram')
        logger.warning('\'subchat\' attribute is the same entity as the \'chat\''
                       + ' field for telegram')
        
        return MultiPlatformSubChat('telegram',
                                    sub_chat.id,
                                    sub_chat.title or sub_chat.full_name)
    
    def convert_to_multi_platform_user(self, user: User,
                                       from_chat: Optional[MultiPlatformChat] = None):
        return MultiPlatformUser('telegram', user.username or user.full_name, from_chat)
    
    def convert_to_multi_platform_message(
        self, message: Message
    ):
        chat = self.convert_to_multi_platform_chat(message.chat)

        author_user = (self.convert_to_multi_platform_user(message.from_user, chat)
                       if message.from_user is not None else None)
        
        return  MultiPlatformMessage(
            'telegram',
            message.id,
            chat,
            self.convert_to_multi_platform_sub_chat(message.chat),
            message.text,
            author_user
        )
    
telegram_entities_converter = TelegramEntitiesConverter()
