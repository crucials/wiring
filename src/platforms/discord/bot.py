import asyncio
from typing import Any, Callable, Optional

import discord

from bot_base import Bot
from platforms.discord.entities_converter import discord_entities_converter
from logging_options import DEFAULT_LOGGING_OPTIONS
from errors.not_messageable import NotMessageableChatError


class CustomClient(discord.Client):
    def __init__(self,
                 intents: discord.Intents,
                 event_handlers: dict[str, Callable]):
        super().__init__(intents=intents)
        self._event_handlers = event_handlers

    async def on_message(self, message: discord.Message):
        if not self.user or message.author.id == self.user.id:
            return

        self.__run_event_handler_if_exists(
            'all', 'message', discord_entities_converter.convert_to_multi_platform_message(message)
        )

        self.__run_event_handler_if_exists(
            'message', discord_entities_converter.convert_to_multi_platform_message(message)
        )

    async def on_member_join(self, member: discord.Member):
        self.__run_event_handler_if_exists(
            'all', 'join', discord_entities_converter.convert_to_multi_platform_user(member)
        )

        self.__run_event_handler_if_exists(
            'join', discord_entities_converter.convert_to_multi_platform_user(member)
        )

    def __run_event_handler_if_exists(self, event: str, *args):
        do_on_event = self._event_handlers.get(event)

        if do_on_event is not None:
            do_on_event(*args)


class DiscordBot(Bot):
    def __init__(self, token: str, logging_options=DEFAULT_LOGGING_OPTIONS):
        super().__init__('discord')

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.client = CustomClient(intents, {
            'all': lambda event, data: self._run_event_handlers(event, data),
            'message': self._check_message_for_command,
        })
        self._token = token

        discord.utils.setup_logging(handler=logging_options['handler']
                                    or discord.utils.MISSING,
                                    level=logging_options['level'])

    async def start(self):
        await self.client.login(self._token)
        self.event_listening_coroutine = asyncio.create_task(self.client.connect())

    async def stop(self):
        await self.client.close()

    async def send_message(self, chat_id: int, text: str,
                           reply_message_id: Optional[int] = None,
                           files: Optional[list] = None):
        channel: Any = await self.client.fetch_channel(chat_id)

        if not hasattr(channel, 'send'):
            raise NotMessageableChatError('discord', channel.id)

        files = [discord.File(file) for file in files or []]

        if reply_message_id is not None:
            message: discord.Message = await channel.fetch_message(reply_message_id)
            await message.reply(text, files=files)
        else:
            await channel.send(text, files=files)

    async def get_chats_from_group(self, chat_group_id: int):
        channels = await (await self.client.fetch_guild(chat_group_id)).fetch_channels()
        return [discord_entities_converter.convert_to_multi_platform_chat(channel)
                for channel in channels]
