import logging
import pytest

from wiring.multi_platform_bot import MultiPlatformBot


logger = logging.getLogger()


@pytest.mark.asyncio(scope='session')
async def test_message_sending(multi_platform_bot: MultiPlatformBot):
    twitch_bots = [bot for bot in multi_platform_bot.platform_bots
                   if bot.platform == 'twitch']

    if len(twitch_bots) == 0:
        logger.warning('skipping twitch bot actions testing because it\'s not added '
                       + 'via TWITCH_BOT_TOKEN environment variable')
        return

    channels = await multi_platform_bot.get_chat_groups('twitch')

    assert len(channels) > 0

    await multi_platform_bot.send_message({
        'twitch': channels[0].id
    }, 'test message')
