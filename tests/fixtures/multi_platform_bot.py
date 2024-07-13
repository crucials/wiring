import asyncio
import os

from dotenv import load_dotenv
import pytest

from tests.errors.missing_environment_variables_error import MissingEnvironmentVariablesError
from wiring.multi_platform_bot import MultiPlatformBot
from wiring.platforms.discord import DiscordBot
from wiring.platforms.telegram import TelegramBot
from wiring.platforms.twitch import TwitchBot


load_dotenv()


class NoBotsAddedError(Exception):
    """at least one platform bot must be added to run tests"""
    def __init__(self):
        super().__init__('at least one platform bot must be added to run tests')


async def cancel_pending_asyncio_tasks(event_loop):
    pending_tasks = [task for task in asyncio.all_tasks(event_loop)
                     if not task.done()]

    for task in pending_tasks:
        task.cancel()

    try:
        await asyncio.wait(pending_tasks)
    except asyncio.exceptions.CancelledError:
        pass


@pytest.fixture(scope='session')
async def multi_platform_bot():
    bot = MultiPlatformBot()

    if 'DISCORD_BOT_TOKEN' in os.environ:
        bot.platform_bots.append(DiscordBot(os.environ['DISCORD_BOT_TOKEN']))

    if 'TELEGRAM_BOT_TOKEN' in os.environ:
        bot.platform_bots.append(TelegramBot(os.environ['TELEGRAM_BOT_TOKEN']))

    if 'TWITCH_BOT_TOKEN' in os.environ:
        testing_channel = os.environ.get('TWITCH_TESTING_CHANNEL')

        if testing_channel is None:
            raise MissingEnvironmentVariablesError(
                'to test twitch bot, you must specify a twitch channel id '
                + 'for testing like that:\nTWITCH_TESTING_CHANNEL=<streamer username>'
            )

        bot.platform_bots.append(TwitchBot(
            os.environ['TWITCH_BOT_TOKEN'],
            streamer_usernames_to_connect=[testing_channel]
        ))

    if len(bot.platform_bots) == 0:
        raise NoBotsAddedError()

    await bot.start()

    yield bot

    await bot.stop()
    await cancel_pending_asyncio_tasks(asyncio.get_event_loop())
