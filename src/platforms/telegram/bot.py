import asyncio
from io import BufferedReader
import logging
from typing import Optional

from telegram.ext import ApplicationBuilder, MessageHandler, ChatMemberHandler
from telegram.error import TelegramError
from telegram import (InputFile, InputMediaAudio, InputMediaDocument,
                      InputMediaPhoto, InputMediaVideo, Update)

from bot_base import Bot
from errors.bot_api_error import BotApiError
from logging_options import DEFAULT_LOGGING_OPTIONS
from platforms.telegram.entities_converter import telegram_entities_converter


class TelegramBot(Bot):
    def __init__(self, token: str, logging_options=DEFAULT_LOGGING_OPTIONS):
        super().__init__('telegram')
        self.client = ApplicationBuilder().token(token).build()

        self.__setup_event_handlers()

        self.logger = logging.getLogger('telegram')

        if logging_options['handler']:
            self.logger.addHandler(logging_options['handler'])
            self.logger.setLevel(logging_options['level'])

    def __setup_event_handlers(self):
        # mess, need to move it to a different module/class
        async def handle_update(update: Update, context):
            if update.message is not None:
                message = telegram_entities_converter.convert_to_multi_platform_message(
                    update.message
                )

                self._run_event_handlers('message', message)

                self._check_message_for_command(message)

                for new_member in update.message.new_chat_members or []:
                    self._run_event_handlers(
                        'join',
                        telegram_entities_converter.convert_to_multi_platform_user(
                            new_member,
                            telegram_entities_converter.convert_to_multi_platform_chat_group(
                                update.message.chat
                            )
                        )
                    )

        # registering the same handler for each needed update
        # because i cant find global update handler solution
        self.client.add_handler(ChatMemberHandler(callback=handle_update))
        self.client.add_handler(MessageHandler(filters=None, callback=handle_update))

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

    async def send_message(self, chat_id, text: str,
                           reply_message_id=None,
                           files: Optional[list[BufferedReader]] = None):
        try:
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
        except TelegramError as telegram_error:
                raise BotApiError('telegram', telegram_error.message)

    async def get_chats_from_group(self, chat_group_id: int):
        return [
            telegram_entities_converter.convert_to_multi_platform_chat(
                await self.client.bot.get_chat(chat_group_id)
            )
        ]

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
