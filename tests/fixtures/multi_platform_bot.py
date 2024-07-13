import asyncio
import logging
import os
from typing import Optional

from dotenv import load_dotenv
import pytest

from wiring.multi_platform_bot import MultiPlatformBot
from wiring.platforms.discord import DiscordBot
from wiring.platforms.telegram import TelegramBot


load_dotenv()


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
    bot.platform_bots = [DiscordBot(os.environ['DISCORD_BOT_TOKEN']),
                         TelegramBot(os.environ['TELEGRAM_BOT_TOKEN'])]

    await bot.start()

    yield bot

    await bot.stop()
    await cancel_pending_asyncio_tasks(asyncio.get_event_loop())
