import asyncio
import logging
import os

from dotenv import load_dotenv

from flectrum import (Bot, MultiPlatformMessage, MultiPlatformBot, MultiPlatformUser,
                      Command)
from flectrum.platforms.discord import DiscordBot
from flectrum.platforms.telegram import TelegramBot
from flectrum.logging_options import LoggingOptions


load_dotenv()

handler = logging.StreamHandler()

logger = logging.getLogger()
logger.addHandler(handler)


async def send_commands_list(bot: Bot, message: MultiPlatformMessage,
                             args: list[str]):
    if message.chat is None:
        return

    await bot.send_message(
        message.chat.id,
        'available commands:\n' + '\n'.join(['/' + command.name.__str__() for command
                                             in bot.commands]),
        reply_message_id=message.id
    )


async def send_greetings(bot: Bot, user: MultiPlatformUser):
    if user.from_chat_group is not None:
        for chat in await bot.get_chats_from_group(user.from_chat_group.id):
            try:
                await bot.send_message(chat.id, 'hi ' + user.username)
            except Exception as error:
                logger.error(error)


async def send_goodbye(bot: Bot, user: MultiPlatformUser):
    if user.from_chat_group is not None:
        for chat in await bot.get_chats_from_group(user.from_chat_group.id):
            try:
                await bot.send_message(chat.id, 'bye ' + user.username)
            except Exception as error:
                logger.error(error)


async def start_bots():
    logging_options: LoggingOptions = {'handler': handler,
                                       'level': logging.INFO}

    bot = MultiPlatformBot(logging_options=logging_options)

    bot.platform_bots = [
        DiscordBot(os.environ['DISCORD_BOT_TOKEN'], logging_options),
        TelegramBot(os.environ['TELEGRAM_BOT_TOKEN'], logging_options)
    ]

    async with bot:
        await bot.setup_commands([
            Command(['start', 'help', 'help1'], send_commands_list)
        ])

        bot.add_event_handler('join', send_greetings)
        bot.add_event_handler('leave', send_goodbye)

        await bot.listen_to_events()


asyncio.run(start_bots())
