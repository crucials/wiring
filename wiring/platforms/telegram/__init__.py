import asyncio
import datetime
from io import BufferedReader
import logging
from typing import Optional

from telegram.ext import ApplicationBuilder, MessageHandler, ChatMemberHandler
from telegram.error import TelegramError
from telegram import (InputFile, InputMediaAudio, InputMediaDocument,
                      InputMediaPhoto, InputMediaVideo, Update)

from wiring.bot_base import Bot
from wiring.errors.action_not_supported_error import ActionNotSupportedError
from wiring.errors.bot_api_error import BotApiError
from wiring.platforms.telegram._entities_converter import telegram_entities_converter


class TelegramBot(Bot):
    def __init__(self, token: str):
        super().__init__('telegram')
        self.client = ApplicationBuilder().token(token).build()

        self.__setup_event_handlers()

        self.logger = logging.getLogger('wiring.telegram')

    def __setup_event_handlers(self):
        # mess, need to move it to a different module/class
        async def handle_update(update: Update, context):
            if update.message is not None:
                multi_platform_chat = (
                    telegram_entities_converter
                    .convert_to_multi_platform_chat_group(update.message.chat)
                )

                multi_platform_message = (
                    telegram_entities_converter
                    .convert_to_multi_platform_message(update.message)
                )

                self._run_event_handlers('message', multi_platform_message)

                self._check_message_for_command(multi_platform_message)

                for new_member in update.message.new_chat_members or []:
                    self._run_event_handlers(
                        'join',
                        telegram_entities_converter.convert_to_multi_platform_user(
                            new_member,
                            multi_platform_chat
                        )
                    )

                if update.message.left_chat_member is not None:
                    self._run_event_handlers(
                        'leave',
                        telegram_entities_converter.convert_to_multi_platform_user(
                            update.message.left_chat_member,
                            multi_platform_chat
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
        if self.client.updater:
            await self.client.updater.stop()
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

    async def get_chat_groups(self, on_platform=None):
        raise ActionNotSupportedError('it seems telegram api does not permit to get '
                                      + 'all chats your bot are member of \n'
                                      + 'what you can do is to keep track of chats '
                                      + 'bot is invited to or is removed from in '
                                      + 'some database with events')

    async def get_chats_from_group(self, chat_group_id: int):
        try:
            return [
                telegram_entities_converter.convert_to_multi_platform_chat(
                    await self.client.bot.get_chat(chat_group_id)
                )
            ]
        except TelegramError as telegram_error:
            raise BotApiError('telegram', telegram_error.message)

    async def ban(self,
                  chat_group_id: int,
                  user_id: int,
                  reason=None,
                  seconds_duration=None):
        try:
            if reason is not None:
                self.logger.warning('ignoring `reason` param for `Bot.ban` method, '
                                    + 'as it\'s not supported in telegram')

            until_date = None

            if seconds_duration is not None:
                until_date = (datetime.datetime.now()
                              + datetime.timedelta(seconds=seconds_duration))

            await self.client.bot.ban_chat_member(chat_group_id, user_id,
                                                  until_date=until_date)
        except TelegramError as telegram_error:
            raise BotApiError('telegram', telegram_error.message)

    async def get_user_by_name(self, username: str, chat_group_id: int):
        raise ActionNotSupportedError('getting users by their usernames is not '
                                      + 'possible on telegram. to be more precise, '
                                      + 'it is impossible to get all users from '
                                      + 'chat group \n'
                                      + 'what you can do is to keep track of new/left'
                                      + 'members with events in some database')

    async def delete_messages(self, chat_id: int, *messages_ids: int):
        try:
            successful = await self.client.bot.delete_messages(chat_id, messages_ids)

            if not successful:
                raise BotApiError('telegram', 'failed to delete messages, perhaps '
                                  + 'you dont have the permission to do this')
        except TelegramError as telegram_error:
            raise BotApiError('telegram', telegram_error.message)

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
