import asyncio
from io import BufferedReader
from typing import Optional

from telegram.ext import ApplicationBuilder, MessageHandler
from telegram import InputMediaPhoto, Message, Update

from bot_base import Bot
from logging_options import DEFAULT_LOGGING_OPTIONS
from multi_platform_resources import MultiPlatformMessage


class TelegramBot(Bot):
    def __init__(self, token: str, logging_options=DEFAULT_LOGGING_OPTIONS):
        super().__init__('telegram')
        self.client = ApplicationBuilder().token(token).build()

        async def handle_message(update: Update, context):
            if update.message:
                await self._check_message_for_command(
                    self.__convert_to_multi_platform_message(update.message)
                )

        self.client.add_handler(MessageHandler(filters=None, callback=handle_message))

        if logging_options['handler']:
            self.client.bot._LOGGER.addHandler(logging_options['handler'])
            self.client.bot._LOGGER.setLevel(logging_options['level'])

    async def start(self):
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

    def __convert_to_multi_platform_message(self, message: Message):
        return MultiPlatformMessage('telegram', message.id, message.chat_id,
                                    message.text or '')

    async def send_message(self, chat_id, text: str,
                           reply_message_id=None,
                           images: Optional[list[BufferedReader]] = None):
        if images is not None:
            await self.client.bot.send_media_group(
                chat_id,
                [InputMediaPhoto(media=image) for image in images],
                caption=text,
                reply_to_message_id=reply_message_id
            )
            return

        await self.client.bot.send_message(chat_id, text,
                                           reply_to_message_id=reply_message_id)
