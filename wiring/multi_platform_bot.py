import logging
from typing import Optional

from wiring.bot_base import Bot, Command, Event
from wiring.logging_options import DEFAULT_LOGGING_OPTIONS
from wiring.multi_platform_resources import MultiPlatformValue, PlatformSpecificValue


class PlatformBotNotFoundError(Exception):
    def __init__(self, requested_platform: str):
        super().__init__(f'bot with platform \'{requested_platform}\' was not added')


class MultiPlatformBot(Bot):
    def __init__(self, logging_options=DEFAULT_LOGGING_OPTIONS):
        super().__init__()
        self.platform_bots: list[Bot] = []

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging_options['level'])

    async def start(self):
        self.logger.info('started')
        for bot in self.platform_bots:
            await bot.start()

    async def stop(self):
        for bot in self.platform_bots:
            await bot.stop()

    async def listen_to_events(self):
        for bot in self.platform_bots:
            if bot.event_listening_coroutine is not None:
                await bot.event_listening_coroutine

    async def send_message(self, chat_id: MultiPlatformValue, text: str,
                           reply_message_id: MultiPlatformValue = {},
                           files: Optional[list] = None):
        for bot in self.platform_bots:
            if bot.platform not in chat_id:
                continue

            platform_chat_id = chat_id.get(bot.platform)
            platform_reply_message_id = reply_message_id.get(bot.platform)

            if platform_chat_id is not None:
                self.logger.info(f'sending message to chat \'{platform_chat_id}\' '
                                 + f'on \'{bot.platform}\'')

                await bot.send_message(platform_chat_id, text,
                                       platform_reply_message_id,
                                       files)

    async def get_chats_from_group(self, chat_group_id: PlatformSpecificValue):
        """fetches chats grouped in some entity like discord server

        Raises:
            PlatformBotNotFoundError: if bot for specified platform was not added
        """
        needed_bots = [bot for bot in self.platform_bots
                       if bot.platform == chat_group_id['platform']]

        if len(needed_bots) == 0:
            raise PlatformBotNotFoundError(chat_group_id['platform'])

        return await needed_bots[0].get_chats_from_group(chat_group_id['value'])

    def add_event_handler(self, event: Event, handler):
        super().add_event_handler(event, handler)
        for bot in self.platform_bots:
            bot.add_event_handler(event, handler)

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        for bot in self.platform_bots:
            await bot.setup_commands(commands, prefix)

        await super().setup_commands(commands, prefix)
