import discord

from wiring.multi_platform_resources import (MultiPlatformChatGroup, MultiPlatformMessage,
                                      MultiPlatformChat, MultiPlatformUser)
from wiring.platforms.discord.channels import MessageableChannel
from wiring._to_multi_platform_converter import ToMultiPlatformConverter


class DiscordEntitiesConverter(ToMultiPlatformConverter):
    def convert_to_multi_platform_chat_group(self, chat_group: discord.Guild):
        return MultiPlatformChatGroup('discord', chat_group.id, chat_group.name)

    def convert_to_multi_platform_chat(
        self, chat: MessageableChannel
    ):
        name = None

        if (not isinstance(chat, discord.PartialMessageable)
                and not isinstance(chat, discord.DMChannel)):
            name = chat.name

        return MultiPlatformChat('discord',
                                 chat.id,
                                 name)

    def convert_to_multi_platform_user(self, user: discord.User | discord.Member):
        if isinstance(user, discord.Member):
            return MultiPlatformUser('discord', user.name,
                                     self.convert_to_multi_platform_chat_group(user.guild))

        return MultiPlatformUser('discord', user.name, None)

    def convert_to_multi_platform_message(
        self, message: discord.Message
    ):
        chat = None

        if message.guild is not None:
            chat = self.convert_to_multi_platform_chat_group(message.guild)

        return MultiPlatformMessage(
            'discord',
            message.id,
            chat,
            self.convert_to_multi_platform_chat(message.channel),
            message.content,
            self.convert_to_multi_platform_user(message.author)
        )


discord_entities_converter = DiscordEntitiesConverter()
