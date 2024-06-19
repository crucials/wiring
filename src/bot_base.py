from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from io import BufferedReader
from typing import Any, Callable, Coroutine, Literal, Optional, Awaitable

from multi_platform_resources import MultiPlatformMessage


CommandHandler = Callable[[Any, MultiPlatformMessage, list[str]], Coroutine]

Event = Literal['message']

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
                 platform: Optional[str] = None):
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
        """
        :param images: images streams to read and embed as a files.
        **closes the streams automatically after reading**
        """
        pass

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        self.commands_prefix = prefix
        self.commands = commands

    def add_event_handler(self, handler: EventHandler):
        self._event_handlers.append(handler)

    async def __aenter__(self):
        await self.start()

    async def __aexit__(self, *args):
        await self.stop()

    def _run_event_handlers(self, event: Event, event_data=None):
        [asyncio.create_task(handler.do_on_event(self, event_data))
         for handler in self._event_handlers
         if handler.event == event]

    def _check_message_for_command(self, message: MultiPlatformMessage):
        def has_command(text: str, command: Command):
            cleaned_text = text.removeprefix(self.commands_prefix).strip().casefold()

            if isinstance(command.name, list):
                return len([name for name in command.name
                            if cleaned_text == name.casefold()]) > 0
            else:
                return command.name.casefold() == cleaned_text

        if not message.content.startswith(self.commands_prefix):
            return
        
        message_parts = message.content.split(' ')

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
