import asyncio
import logging
from typing import Callable, Optional

import twitchio
import twitchio.ext.commands

from wiring._utils.find import find_item
from wiring.bot_base import Bot, Event
from wiring.errors.bot_api_error import BotApiError
from wiring.errors.not_found_error import NotFoundError
from wiring.platforms.twitch._entities_converter import (twitch_entities_converter,
                                                         TwitchMessageWithUser)


class CustomTwitchClient(twitchio.ext.commands.Bot):
    def __init__(self,
                 access_token: str,
                 streamer_usernames_to_connect: list[str],
                 get_commands_prefix: Callable[[], str],
                 do_on_event: Callable):
        self._do_on_event = do_on_event

        self.access_token = access_token

        super().__init__(access_token,
                         prefix=get_commands_prefix,
                         initial_channels=streamer_usernames_to_connect)

    async def event_message(self, message: twitchio.Message):
        if message.echo:
            return

        self._do_on_event(
            'message',
            twitch_entities_converter.convert_to_multi_platform_message(
                TwitchMessageWithUser(message, await message.author.user())
            )
        )


class TwitchBot(Bot):
    def __init__(self,
                 access_token: str,
                 streamer_usernames_to_connect: list[str]):
        """initializes a twitch bot for usage with `MultiPlatformBot` class

        Args:
            access_token: twitch bot api access token
            streamer_usernames_to_connect: twitch bots cannot interact with a chat of
                the specific stream without explicitly connecting to it by the streamer
                username
        """
        super().__init__('twitch')

        self.client = CustomTwitchClient(access_token,
                                         streamer_usernames_to_connect,
                                         lambda: self.commands_prefix,
                                         self._run_event_from_twitch_client)

        self.logger = logging.getLogger('wiring.twitch')

    def _run_event_from_twitch_client(self, event: Event, event_data=None):
        self._run_event_handlers(event, event_data)

        if event == 'message' and event_data is not None:
            self._check_message_for_command(event_data)

    async def start(self):
        self.event_listening_coroutine = asyncio.create_task(self.client.start())

    async def stop(self):
        await self.client.close()

    async def send_message(self,
                           chat_id: str,
                           text,
                           reply_message_id: Optional[int] = None,
                           files=None):
        target_channel = self._get_channel_or_raise(chat_id)

        if reply_message_id is not None or files is not None:
            self.logger.warning('replying to messages and attaching files are not '
                                + 'supported for twitch')

        try:
            await target_channel.send(text)
        except twitchio.InvalidContent:
            raise BotApiError('twitch', 'message contains inappropriate/invalid content')
        except twitchio.TwitchIOException as twitch_error:
            raise BotApiError('twitch', str(twitch_error))

    async def get_chat_groups(self, on_platform=None):
        return [
            twitch_entities_converter.convert_to_multi_platform_chat_group(
                channel
            )
            for channel in self.client.connected_channels
        ]

    async def get_chats_from_group(self, chat_group_id: str):
        channel = self._get_channel_or_raise(chat_group_id)
        return [twitch_entities_converter.convert_to_multi_platform_chat(channel)]

    async def ban(self,
                  chat_group_id: str,
                  user_id: int,
                  reason=None,
                  seconds_duration=None):
        streamer = await self._get_channel_or_raise(chat_group_id).user()

        if self.client.user_id is None:
            return

        try:
            if seconds_duration is None:
                await streamer.ban_user(self.client.access_token,
                                        self.client.user_id,
                                        user_id,
                                        reason or '-')
            else:
                await streamer.timeout_user(self.client.access_token,
                                            self.client.user_id,
                                            user_id,
                                            seconds_duration,
                                            reason or '-')
        except twitchio.TwitchIOException as twitch_error:
            raise BotApiError('twitch', str(twitch_error))

    async def get_user_by_name(self, username: str, chat_group_id: int):
        users = await self.client.fetch_users(names=[username])

        if len(users) == 0:
            return None

        return twitch_entities_converter.convert_to_multi_platform_user(users[0])

    async def delete_messages(self, chat_id: str, *messages_ids: str):
        channel = self._get_channel_or_raise(chat_id)

        try:
            for message_id in messages_ids:
                await channel.send(f'/delete {message_id}')
        except twitchio.TwitchIOException as twitch_error:
            raise BotApiError('twitch', str(twitch_error))

    def _get_channel_or_raise(self, username: str):
        channel = find_item(self.client.connected_channels,
                            lambda channel: channel.name == username)
        if channel is None:
            raise NotFoundError('twitch', 'twitch channel with username '
                                + f'\'{username}\' not found')

        return channel
