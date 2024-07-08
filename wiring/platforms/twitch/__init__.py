import asyncio
import logging
from typing import Callable, Optional

import twitchio
import twitchio.ext.commands

from wiring.bot_base import Bot, Event
from wiring.platforms.twitch._entities_converter import (twitch_entities_converter,
                                                         TwitchMessageWithUser)


class CustomTwitchClient(twitchio.ext.commands.Bot):
    def __init__(self,
                 access_token: str,
                 streamer_usernames_to_connect: list[str],
                 get_commands_prefix: Callable[[], str],
                 do_on_event: Callable):
        self._do_on_event = do_on_event

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
                                         self._run_handlers)

        self.logger = logging.getLogger('wiring.twitch')

    def _run_handlers(self, event: Event, event_data=None):
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
        for channel in self.client.connected_channels:
            if channel.name == chat_id:
                await channel.send(text)
                break

    async def get_chat_groups(self, on_platform=None):
        raise Exception()

    async def get_chats_from_group(self, chat_group_id):
        raise Exception()

    async def ban(self,
                  chat_group_id: int,
                  user_id: int,
                  reason=None,
                  until_date=None):
        ...

    async def get_user_by_name(self, username: str, chat_group_id: int):
        ...
