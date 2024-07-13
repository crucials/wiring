import logging
from typing import Optional

from wiring.bot_base import Bot, Command, Event
from wiring.multi_platform_resources import (MultiPlatformValue, Platform,
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
        bot = MultiPlatformBot()

        bot.platform_bots = [
            DiscordBot(os.environ['DISCORD_BOT_TOKEN']),
            TelegramBot(os.environ['TELEGRAM_BOT_TOKEN'])
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
    def __init__(self):
        super().__init__()
        self.platform_bots: list[Bot] = []

        self.logger = logging.getLogger('wiring.multi_platform')

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
                           reply_message_id: Optional[MultiPlatformValue] = None,
                           files: Optional[list] = None):
        for bot in self.platform_bots:
            if bot.platform not in chat_id:
                continue

            platform_chat_id = chat_id.get(bot.platform)
            platform_reply_message_id = None

            if reply_message_id is not None:
                platform_reply_message_id = reply_message_id.get(bot.platform)

            if platform_chat_id is not None:
                self.logger.info(f'sending message to chat \'{platform_chat_id}\' '
                                 + f'on \'{bot.platform}\'')

                await bot.send_message(platform_chat_id,
                                       text,
                                       platform_reply_message_id,
                                       files)

    async def get_chat_groups(self, on_platform=None):
        if on_platform is None:
            raise ValueError('param `on_platform` must be specified when using '
                             + '`MultiPlatformBot` class')

        needed_bots = self.__get_bots_on_platform(on_platform)
        return await needed_bots[0].get_chat_groups()

    async def get_chats_from_group(self, chat_group_id: PlatformSpecificValue):
        needed_bots = self.__get_bots_on_platform(chat_group_id['platform'])

        return await needed_bots[0].get_chats_from_group(chat_group_id['value'])

    async def ban(self,
                  chat_group_id: MultiPlatformValue,
                  user_id: MultiPlatformValue,
                  reason=None,
                  seconds_duration=None):
        for bot in self.platform_bots:
            if bot.platform not in chat_group_id or bot.platform not in user_id:
                continue

            platform_chat_group_id = chat_group_id[bot.platform]
            platform_user_id = user_id[bot.platform]

            await bot.ban(platform_chat_group_id, platform_user_id, reason,
                          seconds_duration)

    async def get_user_by_name(self,
                               username: PlatformSpecificValue,
                               chat_group_id: PlatformSpecificValue):
        platform_bot = self.__get_bots_on_platform(username['platform'])[0]

        return await platform_bot.get_user_by_name(username['value'],
                                                   chat_group_id['value'])

    async def delete_messages(self,
                              chat_id: MultiPlatformValue,
                              *messages_ids: MultiPlatformValue):
        for bot in self.platform_bots:
            if bot.platform not in chat_id or bot.platform not in messages_ids:
                continue

            self.logger.info(f'deleting message in chat \'{chat_id}\' '
                             + 'on \'{bot.platform}\'')
            await bot.delete_messages(chat_id[bot.platform], *messages_ids[bot.platform])

    def add_event_handler(self, event: Event, handler):
        super().add_event_handler(event, handler)
        for bot in self.platform_bots:
            bot.add_event_handler(event, handler)

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        for bot in self.platform_bots:
            await bot.setup_commands(commands, prefix)

        await super().setup_commands(commands, prefix)

    def __get_bots_on_platform(self, platform: Platform):
        needed_bots = [bot for bot in self.platform_bots
                       if bot.platform == platform]

        if len(needed_bots) == 0:
            raise PlatformBotNotFoundError(platform)

        return needed_bots
