import logging
from typing import Optional

from wiring.bot_base import Bot, Command, Event
from wiring.logging_options import DEFAULT_LOGGING_OPTIONS
from wiring.multi_platform_resources import (MultiPlatformValue,
                                             PlatformSpecificValue)


class PlatformBotNotFoundError(Exception):
    def __init__(self, requested_platform: str):
        super().__init__(f'bot with platform \'{requested_platform}\' was not added')


class MultiPlatformBot(Bot):
    """bot that aggregates bots with specific platform (e.g. `DiscordBot`, `Telegram`)

    when calling some action, for example `ban` method, this class accepts
    platform-dependent params like `user_id` as a dictionary
    that contains a value for each optional platform (for example:
    `{'discord': '1u2412dfsadf', 'telegram': '28ud2da_&546'}`). then it calls needed
    action in first found bot with matched platform

    Initializing example:
        ```
        bot = MultiPlatformBot(logging_options=logging_options)

        bot.platform_bots = [
            DiscordBot(os.environ['DISCORD_BOT_TOKEN'], logging_options),
            TelegramBot(os.environ['TELEGRAM_BOT_TOKEN'], logging_options)
        ]

        async with bot:
            ...
        ```

    Sending message example:
        ```
        async with bot:
            await bot.send_message(chat_id={'discord': '123', 'telegram': '321'},
                                   text='test message')
        ```
    """
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
        needed_bots = self.__get_bots_on_platform(chat_group_id['platform'])

        return await needed_bots[0].get_chats_from_group(chat_group_id['value'])

    async def ban(self,
                  chat_group_id: MultiPlatformValue,
                  user_id: MultiPlatformValue,
                  reason=None,
                  until_date=None):
        for bot in self.platform_bots:
            if bot.platform not in chat_group_id or bot.platform not in user_id:
                continue

            platform_chat_group_id = chat_group_id[bot.platform]
            platform_user_id = user_id[bot.platform]

            await bot.ban(platform_chat_group_id, platform_user_id, reason,
                          until_date)

    async def get_user_by_name(self,
                               username: PlatformSpecificValue,
                               chat_group_id: PlatformSpecificValue):
        platform_bot = self.__get_bots_on_platform(username['platform'])[0]

        return await platform_bot.get_user_by_name(username['value'],
                                                   chat_group_id['value'])

    def add_event_handler(self, event: Event, handler):
        super().add_event_handler(event, handler)
        for bot in self.platform_bots:
            bot.add_event_handler(event, handler)

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        for bot in self.platform_bots:
            await bot.setup_commands(commands, prefix)

        await super().setup_commands(commands, prefix)

    def __get_bots_on_platform(self, platform: str):
        needed_bots = [bot for bot in self.platform_bots
                       if bot.platform == platform]

        if len(needed_bots) == 0:
            raise PlatformBotNotFoundError(platform)

        return needed_bots
