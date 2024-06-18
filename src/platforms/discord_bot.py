import asyncio
from typing import Any, Optional

import discord

from bot_base import Bot
from logging_options import DEFAULT_LOGGING_OPTIONS
from multi_platform_resources import MultiPlatformMessage


class CustomClient(discord.Client):
    def __init__(self,
                 intents: discord.Intents,
                 event_handlers: dict):
        super().__init__(intents=intents)
        self._event_handlers = event_handlers

    async def on_message(self, message: discord.Message):
        do_on_message = self._event_handlers.get('message')
        if do_on_message is not None:
            await do_on_message(self.convert_to_multi_platform_message(message))

    def convert_to_multi_platform_message(self, discord_message: discord.Message):
        return MultiPlatformMessage('discord', discord_message.id,
                                    discord_message.channel.id,
                                    discord_message.content)


class DiscordBot(Bot):
    def __init__(self, token: str, logging_options=DEFAULT_LOGGING_OPTIONS):
        super().__init__('discord')

        intents = discord.Intents.default()
        intents.message_content = True

        self.client = CustomClient(intents, {
            'message': self._check_message_for_command
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
                           images: Optional[list] = None):
        channel: Any = await self.client.fetch_channel(chat_id)

        files = [discord.File(image) for image in images or []]

        if reply_message_id is not None:
            message: discord.Message = await channel.fetch_message(reply_message_id)
            await message.reply(text, files=files)
        else:
            await channel.send(text, files=files)
