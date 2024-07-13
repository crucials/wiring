import pytest

from wiring.multi_platform_bot import MultiPlatformBot


@pytest.mark.asyncio(scope='session')
async def test_message_sending(multi_platform_bot: MultiPlatformBot):
    channels = await multi_platform_bot.get_chat_groups('twitch')

    assert len(channels) > 0

    await multi_platform_bot.send_message({
        'twitch': channels[0].id
    }, 'test message')
