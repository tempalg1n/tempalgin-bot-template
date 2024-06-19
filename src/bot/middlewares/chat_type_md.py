from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, Message, TelegramObject, User
from aiogram_dialog.api.entities import DialogUpdateEvent

from src.bot.structures.data_structure import TransferData


class ChatTypeMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery | DialogUpdateEvent,
            data: TransferData,
    ) -> Any:
        """This method calls each update of Message or CallbackQuery type."""
        if hasattr(event, 'message'):
            bot: Bot = data['bot']
            bot_instance: User = await bot.get_me()
            if event.message:
                if event.message.chat.type == 'private':
                    return await handler(event, data)
                elif event.message.chat.type in ['group', 'supergroup']:
                    if (
                            event.message.reply_to_message
                            and event.message.reply_to_message.from_user.id == bot_instance.id
                    ):
                        return await handler(event, data)
                    if event.message.caption:
                        message: str = event.message.caption
                    elif event.message.text:
                        message: str = event.message.text
                    elif hasattr(event.message, 'message_text'):
                        if event.message.message_text:
                            message: str = event.message.message_text
                        else:
                            return
                    else:
                        return
                    if bot_instance.username not in message:
                        return
        return await handler(event, data)
