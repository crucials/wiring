# get started

## installation

install the base library:

```sh
pip install wiring
```

then choose extra dependencies for platforms you want your bot to run on.

this command installs dependencies **for all available platforms**:

```sh
pip install wiring[discord] wiring[telegram] wiring[twitch]
```

this guide will run bots on discord and telegram

## running the bots

this library uses python asyncio, learning its fundamentals will make this guide
easier to understand

firstly, prepare your tokens/credentials for each platform your bot gonna run on:

```python
DISCORD_TOKEN = 'place your token here or better load it from enviroment variables'
TELEGRAM_TOKEN = 'place your token here or better load it from enviroment variables'
```

then import needed classes and define commands/event handlers:

```python
from wiring import (Bot, MultiPlatformMessage, MultiPlatformBot, MultiPlatformUser,
                    Command)
from wiring.errors.not_messageable_chat_error import NotMessageableChatError
from wiring.platforms.discord import DiscordBot
from wiring.platforms.telegram import TelegramBot

# triggers on '/test'
async def send_test_message(bot: Bot, message: MultiPlatformMessage,
                             args: list[str]):
    if message.chat is None:
        return

    await bot.send_message(
        message.chat.id,
        'test message',
        reply_message_id=message.id
    )


async def send_greetings(bot: Bot, user: MultiPlatformUser):
    if user.from_chat_group is not None:
        for chat in await bot.get_chats_from_group(user.from_chat_group.id):
            try:
                await bot.send_message(chat.id, 'hi ' + user.username)
            except NotMessageableChatError:
                pass
```

after that, create an entrypoint where the bot starts and run it in event loop:

```python
async def start_bots():
    bot = MultiPlatformBot()

    # registers platforms your bot will run on
    bot.platform_bots = [
        DiscordBot(DISCORD_TOKEN),
        TelegramBot(TELEGRAM_TOKEN),
    ]

    # after entering 'async with', starts connecting to chosen platforms
    async with bot:
        await bot.setup_commands([
            Command('test', send_commands_list),
        ])

        bot.add_event_handler('join', send_greetings)

        # awaiting coroutine that listens to events until the app is somehow stopped,
        # so the app hangs here
        await bot.listen_to_events()


asyncio.run(start_bots())
```

that's all. check out [methods section](./methods.md) to see what the bot can do
and also [events section](./events.md)
