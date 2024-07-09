import logging

import twitchio


from wiring._to_multi_platform_converter import ToMultiPlatformConverter
from wiring.multi_platform_resources import (MultiPlatformChat,
                                             MultiPlatformChatGroup,
                                             MultiPlatformMessage,
                                             MultiPlatformUser)


class TwitchMessageWithUser:
    def __init__(self, message: twitchio.Message, user: twitchio.User):
        self.id = message.id
        self.text = message.content
        self.channel = message.channel
        self.user = user


class TwitchEntitiesConverter(ToMultiPlatformConverter):
    def convert_to_multi_platform_chat_group(self, chat_group: twitchio.Channel):
        logger = logging.getLogger('wiring.twitch')
        logger.warning('chat group is the same entity as the chat for twitch')

        return MultiPlatformChatGroup('twitch', chat_group.name, chat_group.name)

    def convert_to_multi_platform_chat(self, chat: twitchio.Channel):
        return MultiPlatformChat('twitch', chat.name, chat.name)

    def convert_to_multi_platform_message(self, message: TwitchMessageWithUser):
        return MultiPlatformMessage(
            'twitch',
            message.id,
            self.convert_to_multi_platform_chat_group(message.channel),
            self.convert_to_multi_platform_chat(message.channel),
            message.text,
            self.convert_to_multi_platform_user(message.user)
        )

    def convert_to_multi_platform_user(self,
                                       user: twitchio.User):
        from_chat_group = None

        if user.channel is not None:
            from_chat_group = self.convert_to_multi_platform_chat_group(user.channel)

        return MultiPlatformUser('twitch', user.id, user.name, from_chat_group)


twitch_entities_converter = TwitchEntitiesConverter()
