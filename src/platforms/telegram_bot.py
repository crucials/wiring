import asyncio

from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler
from telegram import Message, Update, BotCommand

from bot_base import Bot, Command
from multi_platform_resources import MultiPlatformMessage


class TelegramBot(Bot):
    def __init__(self, token: str):
        super().__init__('telegram')
        self.client = ApplicationBuilder().token(token).build()

        async def handle_message(update: Update, context):
            if update.message:
                await self._check_message_for_command(
                    self.__convert_to_multi_platform_message(update.message)
                )

        self.client.add_handler(MessageHandler(filters=None, callback=handle_message))

    async def start(self):
        print('starting telegram bot')
        await self.client.initialize()

        if self.client.updater is None:
            raise Exception('cant start polling in telegram bot.'
                            + '\'client.updater\' attribute is \'None\'')

        try:
            self.event_listening_coroutine = asyncio.create_task(
                self.client.updater.start_polling()
            )
            await self.client.start()
        except Exception:
            await self.client.stop()

    async def stop(self):
        await self.client.stop()
        await self.client.shutdown()

    async def setup_commands(self, commands: list[Command], prefix: str = '/'):
        self.commands = commands
        self.prefix = prefix

    def __convert_to_multi_platform_message(self, message: Message):
        return MultiPlatformMessage('telegram', message.id, message.chat_id,
                                    message.text or '')

    async def send_message(self, chat_id, text: str, reply_message_id = None):
        await self.client.bot.send_message(chat_id, text,
                                           reply_to_message_id=reply_message_id)
