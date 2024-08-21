import pytest

from wiring.multi_platform_bot import MultiPlatformBot


@pytest.mark.asyncio(scope="session")
async def test_message_sending(multi_platform_bot: MultiPlatformBot):
    twitch_bots = [
        bot for bot in multi_platform_bot.platform_bots if bot.platform == "twitch"
    ]

    if len(twitch_bots) == 0:
        pytest.skip(
            "skipping twitch bot actions testing because it's not added "
            + "via TWITCH_BOT_TOKEN environment variable"
        )

    channels = await multi_platform_bot.get_chat_groups("twitch")

    assert len(channels) > 0, "bot is not connected to any twitch chat"

    await multi_platform_bot.send_message({"twitch": channels[0].id}, "test message")
