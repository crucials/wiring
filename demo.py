import asyncio
import logging
import os

from dotenv import load_dotenv

from wiring import (Bot, MultiPlatformMessage, MultiPlatformBot, MultiPlatformUser,
                    Command)
from wiring.errors.action_not_supported_error import ActionNotSupportedError
from wiring.platforms.discord import DiscordBot
from wiring.platforms.telegram import TelegramBot


load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: [%(levelname)s] %(name)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


async def send_commands_list(bot: Bot, message: MultiPlatformMessage,
                             args: list[str]):
    if message.chat is None:
        return

    await bot.send_message(
        message.chat.id,
        'available commands:\n' + '\n'.join(['/' + str(command.name) for command
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


async def ban(bot: Bot, message: MultiPlatformMessage, args: list[str]):
    if message.chat is None or message.chat_group is None:
        return

    if len(args) < 1:
        await bot.send_message(message.chat.id, 'specify a name/id of a user',
                               reply_message_id=message.id)
        return

    try:
        user = await bot.get_user_by_name(args[0].removeprefix('@'),
                                          message.chat_group.id)

        if user is not None:
            await bot.ban(message.chat_group.id, user.id, None)
            await bot.send_message(message.chat.id, 'banned',
                                   reply_message_id=message.id)
        else:
            await bot.send_message(message.chat.id, 'cant find the user',
                                   reply_message_id=message.id)
    except ActionNotSupportedError:
        await bot.send_message(message.chat.id, 'banning is not supported here',
                               reply_message_id=message.id)


async def send_goodbye(bot: Bot, user: MultiPlatformUser):
    if user.from_chat_group is not None:
        for chat in await bot.get_chats_from_group(user.from_chat_group.id):
            try:
                await bot.send_message(chat.id, 'bye ' + user.username)
            except Exception as error:
                logger.error(error)


async def start_bots():
    bot = MultiPlatformBot()

    bot.platform_bots = [
        DiscordBot(os.environ['DISCORD_BOT_TOKEN']),
        TelegramBot(os.environ['TELEGRAM_BOT_TOKEN'])
    ]

    async with bot:
        await bot.setup_commands([
            Command(['start', 'help', 'help1'], send_commands_list),
            Command('ban-user', ban)
        ])

        bot.add_event_handler('join', send_greetings)
        bot.add_event_handler('leave', send_goodbye)

        await bot.listen_to_events()


asyncio.run(start_bots())
