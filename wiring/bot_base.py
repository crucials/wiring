from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from io import BufferedReader
from typing import Any, Callable, Coroutine, Literal, Optional, Awaitable

from wiring.multi_platform_resources import (MultiPlatformChatGroup, MultiPlatformMessage,
                                             MultiPlatformChat, MultiPlatformUser,
                                             Platform)


CommandHandler = Callable[[Any, MultiPlatformMessage, list[str]], Coroutine]

Event = Literal['message', 'join', 'leave']


@dataclass
class Command:
    name: list[str] | str
    handler: CommandHandler


@dataclass
class EventHandler:
    event: Event
    do_on_event: Callable[[Any, Any], Coroutine]


class Bot(ABC):
    def __init__(self,
                 platform: Optional[Platform] = None):
        self.platform = platform
        self.commands_prefix = '/'
        self.commands = []

        self.event_listening_coroutine: Optional[Awaitable] = None

        self._event_handlers: list[EventHandler] = []

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def send_message(self, chat_id,
                           text: str,
                           reply_message_id: Any = None,
                           files: Optional[list[BufferedReader]] = None):
        """sends message in the chat

        Args:
            files (list): (optional) images streams to read and embed as a files.
                **closes the streams automatically after reading**

        Raises:
            NotMessageableChatError: if message cant be sent in target chat
            BotApiError: if error occurred on some platform api interaction
            ValueError: the files list is not of the appropriate size
        """

    @abstractmethod
    async def get_chat_groups(
        self, on_platform: Optional[Platform] = None
    ) -> list[MultiPlatformChatGroup]:
        """fetches chat groups the bot is member of

        Args:
            on_platform: on what platform bot to use, must be specified only **when
                calling this method from `MultiPlatformBot` class**

        Returns:
            list of chat groups. if target platform doesnt support
            chat groups, they are considered identical to chats,
            so it returns chats converted chat groups

        Raises:
            BotApiError: if error occurred on some platform api interactions
            PlatformBotNotFoundError: if bot for specified platform was
                not added when using `MultiPlatformBot` subclass
            ValueError: if `on_platform` param is not specified when using
                `MultiPlatformBot` class
            ActionNotSupported: if this action is not implemented or is impossible
                for some platforms like telegram
        """

    @abstractmethod
    async def get_chats_from_group(self, chat_group_id) -> list[MultiPlatformChat]:
        """fetches a group of connected chats, for example, a discord server

        Returns:
            list of chats from specified group. if target platform doesnt support
            chat groups, they are considered identical to chats,
            so it returns list of one chat converted from request chat group

        Raises:
            NotFoundError: if some resource cannot be found, subclass of `BotApiError`
            BotApiError: if error occurred on some platform api interaction
            PlatformBotNotFoundError: if bot for specified platform was
                not added when using `MultiPlatformBot` subclass
        """

    @abstractmethod
    async def ban(self, chat_group_id, user_id, reason: Optional[str] = None,
                  seconds_duration: Optional[int] = None):
        """bans the user from the specified chat group

        Args:
            chat_group_id: id of the chat group entity (like a discord server
                or a telegram chat) where to ban
            user_id: id of the user to be banned
            reason: ban reason, not supported on some platforms like telegram
            seconds_duration: seconds until user gets unbanned. if set `None`,
                bans permanently

        Raises:
            NotFoundError: if some resource cannot be found, subclass of `BotApiError`
            BotApiError: if error occurred on platform api interaction. for example,
                if you dont have a permission to ban
        """

    @abstractmethod
    async def get_user_by_name(self,
                               username,
                               chat_group_id) -> Optional[MultiPlatformUser]:
        """get user that takes part in specified chat group by username

        Args:
            username (str): username without prefixes like '@'
            chat_group_id: id of chat group where to search for user

        Raises:
            NotFoundError: if user cannot be found, subclass of `BotApiError`
            BotApiError: if error occurred on platform api interaction. for example,
                if you cant access specified chat group
            ActionNotSupported: if this action is not implemented or is impossible
                for some platforms like telegram
        """

    @abstractmethod
    async def delete_messages(self, chat_id, *messages_ids):
        """deletes messages by their ids

        Raises:
            NotFoundError: if specified chat or message not found
            NotMessageableChatError: if target chat cannot contain messages
            BotApiError: if some other error occurred on platform api interaction, for
                example if you dont have the permission to delete specific message
        """

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        self.commands_prefix = prefix
        self.commands = commands

    def add_event_handler(self, event: Event, handler: Callable[[Any, Any], Coroutine]):
        """
        adds a handler function that will be called when specified event occurs
            with `Bot` object and event data as arguments

        supported events:
            - `message` - when a message sent in any chat bot are member of.
                ignores current bot's messages to prevent recursion
            - `join` - when someone joins in chat/chat group bot are member of
            - `leave` - when someone leaves the chat/chat group bot are member of
        """
        self._event_handlers.append(EventHandler(event, handler))

    async def __aenter__(self):
        await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    def _run_event_handlers(self, event: Event, event_data=None):
        for handler in self._event_handlers:
            if handler.event == event:
                asyncio.create_task(handler.do_on_event(self, event_data))

    def _check_message_for_command(self, message: MultiPlatformMessage):
        def has_command(text: str, command: Command):
            cleaned_text = text.removeprefix(self.commands_prefix).strip().casefold()

            if isinstance(command.name, list):
                return len([name for name in command.name
                            if cleaned_text == name.casefold()]) > 0

            return command.name.casefold() == cleaned_text

        if not message.text or not message.text.startswith(self.commands_prefix):
            return

        message_parts = message.text.split(' ')

        if len(message_parts) == 0:
            return

        matched_commands = [
            some_command for some_command in self.commands
            if has_command(message_parts[0], some_command)
        ]

        if len(matched_commands) > 0:
            asyncio.create_task(
                matched_commands[0].handler(self, message, message_parts[1:])
            )
