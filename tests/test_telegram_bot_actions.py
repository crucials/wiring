import os
import pytest

from tests.errors.missing_environment_variables_error import MissingEnvironmentVariablesError
from wiring.multi_platform_bot import MultiPlatformBot


@pytest.mark.asyncio(scope='session')
async def test_message_sending(multi_platform_bot: MultiPlatformBot):
    telegram_bots = [bot for bot in multi_platform_bot.platform_bots
                     if bot.platform == 'telegram']

    if len(telegram_bots) == 0:
        pytest.skip('skipping telegram bot actions testing because it\'s not added '
                    + 'via TELEGRAM_BOT_TOKEN environment variable')

    testing_chat_id = os.environ.get('TELEGRAM_TESTING_CHAT_ID')

    if testing_chat_id is None:
        raise MissingEnvironmentVariablesError('it\'s not possible to get current '
                                               + 'bot chats with telegram api. so '
                                               + 'you must specify some testing chat id '
                                               + 'in `.env` file like that: '
                                               + 'TELEGRAM_TESTING_CHAT_ID=<id here>')

    await multi_platform_bot.send_message({
        'telegram': int(testing_chat_id)
    }, 'test message')
