from typing import Optional

from bot_base import Bot, Command
from multi_platform_resources import MultiPlatformValue
from platforms.discord_bot import DiscordBot
from platforms.telegram_bot import TelegramBot


class MultiPlatformBot(Bot):
    def __init__(self,
                 commands_prefix: str = '/',
                 commands: list[Command] = []):
        self.commands_prefix = commands_prefix
        self.commands = commands
        self.platform_bots: list[Bot] = []

    async def start(self):
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
                           images: Optional[list] = None):
        for bot in self.platform_bots:
            if bot.platform not in chat_id:
                continue

            platform_chat_id = chat_id.get(bot.platform)
            platform_reply_message_id = reply_message_id.get(bot.platform)

            print(f'sending to {platform_chat_id} on {bot.platform}')

            if platform_chat_id is not None:
                await bot.send_message(platform_chat_id, text,
                                       platform_reply_message_id,
                                       images)

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        for bot in self.platform_bots:
            await bot.setup_commands(commands, prefix)

        await super().setup_commands(commands, prefix)

    def add_discord_bot(self, token: str):
        self.platform_bots.append(
            DiscordBot(token)
        )

    def add_telegram_bot(self, token: str):
        self.platform_bots.append(
            TelegramBot(token)
        )
