from typing import Any

import discord
import discord.channel

from multi_platform_resources import MultiPlatformChat, MultiPlatformMessage, MultiPlatformSubChat, MultiPlatformUser
from to_multi_platform_converter import ToMultiPlatformConverter


class DiscordEntitiesConverter(ToMultiPlatformConverter):
    def convert_to_multi_platform_chat(self, chat: discord.Guild):
        return MultiPlatformChat('discord', chat.id, chat.name)
    
    def convert_to_multi_platform_sub_chat(
        self, sub_chat: discord.channel.PartialMessageable | Any
    ):
        name = None

        if (not isinstance(sub_chat, discord.DMChannel)
            and not isinstance(sub_chat, discord.PartialMessageable)):
            name = sub_chat.name

        return MultiPlatformSubChat('discord', sub_chat.id, name)
    
    def convert_to_multi_platform_user(self, user: discord.User | discord.Member):
        if isinstance(user, discord.Member):
            return MultiPlatformUser('discord', user.name,
                                     self.convert_to_multi_platform_chat(user.guild))

        return MultiPlatformUser('discord', user.name, None)
    
    def convert_to_multi_platform_message(
        self, message: discord.Message
    ):
        chat = None

        if message.guild is not None:
            chat = self.convert_to_multi_platform_chat(message.guild)

        return  MultiPlatformMessage(
            'discord',
            message.id,
            chat,
            self.convert_to_multi_platform_sub_chat(message.channel),
            message.content,
            self.convert_to_multi_platform_user(message.author)
        )
    
discord_entities_converter = DiscordEntitiesConverter()
