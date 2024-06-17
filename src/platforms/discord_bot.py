import asyncio
from typing import Any, Optional

import discord

from bot_base import Bot, Command
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
    def __init__(self, token: str):
        super().__init__('discord')

        intents = discord.Intents.default()
        intents.message_content = True

        self.client = CustomClient(intents, {
            'message': self._check_message_for_command
        })
        self._token = token

    async def start(self):
        await self.client.login(self._token)
        self.event_listening_coroutine = asyncio.create_task(self.client.connect())
        print('started discord bot with token ' + self._token)

    async def stop(self):
        await self.client.close()
        print('stopping discord bot')

    async def send_message(self, chat_id: int, text: str,
                           reply_message_id: Optional[int] = None):
        channel: Any = await self.client.fetch_channel(chat_id)

        if reply_message_id is not None:
            message: discord.Message = await channel.fetch_message(reply_message_id)
            await message.reply(text)
        else:
            await channel.send(text)
