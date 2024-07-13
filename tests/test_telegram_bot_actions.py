import os
import pytest

from wiring.multi_platform_bot import MultiPlatformBot


@pytest.mark.asyncio(scope='session')
async def test_message_sending(multi_platform_bot: MultiPlatformBot):
    testing_chat_id = os.environ.get('TELEGRAM_TESTING_CHAT_ID')

    if testing_chat_id is None:
        raise TypeError('it\'s not possible to get current bot chats with '
                        + 'telegram api. so you must specify some testing chat id '
                        + 'in `.env` file like that: '
                        + 'TELEGRAM_TESTING_CHAT_ID=<id here>')
    
    await multi_platform_bot.send_message({
        'telegram': int(testing_chat_id)
    }, 'test message')
