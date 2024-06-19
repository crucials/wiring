import asyncio
from io import BufferedReader
from typing import Optional

from telegram.ext import ApplicationBuilder, MessageHandler
from telegram import InputFile, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo, Message, Update

from bot_base import Bot
from logging_options import DEFAULT_LOGGING_OPTIONS
from multi_platform_resources import MultiPlatformMessage


class TelegramBot(Bot):
    def __init__(self, token: str, logging_options=DEFAULT_LOGGING_OPTIONS):
        super().__init__('telegram')
        self.client = ApplicationBuilder().token(token).build()
        
        self.__setup_event_handlers()

        if logging_options['handler']:
            self.client.bot._LOGGER.addHandler(logging_options['handler'])
            self.client.bot._LOGGER.setLevel(logging_options['level'])

    def __setup_event_handlers(self):
        async def handle_message(update: Update, context):
            if update.message:
                message = self.__convert_to_multi_platform_message(update.message)

                self._run_event_handlers('message', message)
                
                self._check_message_for_command(message)

        self.client.add_handler(MessageHandler(filters=None, callback=handle_message))

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
                           files: Optional[list[BufferedReader]] = None):
        if files is not None:
            await self.client.bot.send_media_group(
                chat_id,
                [self.__convert_stream_to_telegram_media(file) for file in files],
                caption=text,
                reply_to_message_id=reply_message_id
            )
            return

        await self.client.bot.send_message(chat_id, text,
                                           reply_to_message_id=reply_message_id)
        
    def __convert_stream_to_telegram_media(self, stream: BufferedReader):
            file = InputFile(stream)
            mimetype = file.mimetype
            
            if mimetype.startswith('video'):
                return InputMediaVideo(media=file.input_file_content)
            elif mimetype.startswith('image'):
                return InputMediaPhoto(media=file.input_file_content)
            elif mimetype.startswith('audio'):
                return InputMediaAudio(media=file.input_file_content)
            else:
                return InputMediaDocument(media=file.input_file_content)
