import logging
from typing import Optional

from bot_base import Bot, Command, EventHandler
from logging_options import DEFAULT_LOGGING_OPTIONS
from multi_platform_resources import MultiPlatformValue


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
                
    def add_event_handler(self, handler: EventHandler):
        super().add_event_handler(handler)
        for bot in self.platform_bots:
            bot.add_event_handler(handler)

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        for bot in self.platform_bots:
            await bot.setup_commands(commands, prefix)

        await super().setup_commands(commands, prefix)
