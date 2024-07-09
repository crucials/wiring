import asyncio
import datetime
import logging
from typing import Any, Callable, Optional

import discord

from wiring.bot_base import Bot
from wiring.errors.bot_api_error import BotApiError
from wiring.errors.not_found_error import NotFoundError
from wiring.platforms.discord._entities_converter import discord_entities_converter
from wiring.errors.not_messageable_chat_error import NotMessageableChatError


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

    async def on_member_remove(self, member: discord.Member):
        multi_platform_user = (discord_entities_converter
                               .convert_to_multi_platform_user(member))

        self.__run_event_handler_if_exists(
            'all', 'leave', multi_platform_user
        )

        self.__run_event_handler_if_exists(
            'leave', multi_platform_user
        )

    def __run_event_handler_if_exists(self, event: str, *args):
        do_on_event = self._event_handlers.get(event)

        if do_on_event is not None:
            do_on_event(*args)


class DiscordBot(Bot):
    def __init__(self, token: str):
        super().__init__('discord')

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.client = CustomClient(intents, {
            'all': lambda event, data: self._run_event_handlers(event, data),
            'message': self._check_message_for_command,
        })
        self._token = token

        self.logger = logging.getLogger('wiring.discord')

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

        try:
            if reply_message_id is not None:
                message: discord.Message = await channel.fetch_message(reply_message_id)
                await message.reply(text, files=files)
            else:
                await channel.send(text, files=files)
        except discord.NotFound as discord_not_found_error:
            raise NotFoundError('discord', discord_not_found_error.text)
        except discord.HTTPException as discord_error:
            raise BotApiError('discord', discord_error.text, discord_error.status)

    async def get_chat_groups(self, on_platform=None):
        guilds = [guild async for guild in self.client.fetch_guilds(limit=None)]

        return [
            discord_entities_converter.convert_to_multi_platform_chat_group(guild)
            for guild in guilds
        ]

    async def get_chats_from_group(self, chat_group_id: int):
        try:
            channels = await (await self.client.fetch_guild(chat_group_id)).fetch_channels()
            return [discord_entities_converter.convert_to_multi_platform_chat(channel)
                    for channel in channels]
        except discord.NotFound as discord_not_found_error:
            raise NotFoundError('discord', discord_not_found_error.text)
        except discord.HTTPException as discord_http_error:
            raise BotApiError('discord', discord_http_error.text,
                              discord_http_error.status)
        except discord.errors.InvalidData:
            raise BotApiError('discord', 'received invalid data from api')

    async def ban(self,
                  chat_group_id: int,
                  user_id: int,
                  reason=None,
                  seconds_duration=None):
        try:
            guild = await self.client.fetch_guild(chat_group_id)
            member_to_ban = await guild.fetch_member(user_id)

            if seconds_duration is not None:
                await member_to_ban.timeout(datetime.timedelta(seconds=seconds_duration),
                                            reason=reason)
            else:
                await member_to_ban.ban(reason=reason)
        except discord.NotFound as discord_not_found_error:
            raise NotFoundError('discord', discord_not_found_error.text)
        except discord.HTTPException as discord_http_error:
            raise BotApiError('discord', discord_http_error.text,
                              discord_http_error.status)

    async def get_user_by_name(self, username: str, chat_group_id: int):
        try:
            guild = await self.client.fetch_guild(chat_group_id)
            member = await discord.utils.get(guild.fetch_members(limit=None),
                                             name=username)

            if member is None:
                return None

            return discord_entities_converter.convert_to_multi_platform_user(member)
        except discord.NotFound as discord_not_found_error:
            raise NotFoundError('discord', discord_not_found_error.text)
        except discord.HTTPException as discord_http_error:
            raise BotApiError('discord', discord_http_error.text,
                              discord_http_error.status)

    async def delete_messages(self, chat_id: int, *messages_ids: int):
        try:
            channel: Any = await self.client.fetch_channel(chat_id)

            if not hasattr(channel, 'fetch_message'):
                raise NotMessageableChatError('discord', channel.id)

            for message_id in messages_ids:
                message = await channel.fetch_message(message_id)
                await message.delete()
        except discord.NotFound as discord_not_found_error:
            raise NotFoundError('discord', discord_not_found_error.text)
        except discord.HTTPException as discord_http_error:
            raise BotApiError('discord', discord_http_error.text,
                              discord_http_error.status)
