import logging

import pytest

from tests.errors.unusable_bot_error import UnusableBotError
from wiring.errors.not_messageable_chat_error import NotMessageableChatError
from wiring.multi_platform_bot import MultiPlatformBot


logger = logging.getLogger()


@pytest.mark.asyncio(scope="session")
async def test_message_sending(multi_platform_bot: MultiPlatformBot):
    discord_bots = [
        bot for bot in multi_platform_bot.platform_bots if bot.platform == "discord"
    ]

    if len(discord_bots) == 0:
        pytest.skip(
            "skipping discord bot actions testing because it's not added "
            + "via DISCORD_BOT_TOKEN environment variable"
        )

    guilds = await multi_platform_bot.get_chat_groups("discord")

    if len(guilds) == 0:
        raise UnusableBotError(
            "current discord bot must be at least in one guild to " + "run this test"
        )

    channels = await multi_platform_bot.get_chats_from_group(
        {"platform": "discord", "value": guilds[0].id}
    )
    assert len(channels) > 0, f"got no channels from guild {guilds[0].id}"

    guild_has_messageable_channels = False

    for channel in channels:
        try:
            await multi_platform_bot.send_message(
                {"discord": channel.id}, "test message"
            )

            guild_has_messageable_channels = True
            break
        except NotMessageableChatError:
            logger.debug(f"channel '{channel.name}' cant be messaged")

    if not guild_has_messageable_channels:
        raise UnusableBotError(
            "current discord bot first guild must have a " + "messageable channel"
        )
