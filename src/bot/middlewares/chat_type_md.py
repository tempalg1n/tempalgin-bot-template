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
        if isinstance(event, CallbackQuery) or isinstance(
            event, DialogUpdateEvent
        ):
            return await handler(event, data)

        if isinstance(event, Message):
            bot: Bot = data['bot']
            bot_instance: User = await bot.get_me()
            if event.chat.type == 'private':
                return await handler(event, data)
            elif event.chat.type in ['group', 'supergroup']:
                if (
                    event.reply_to_message
                    and event.reply_to_message.from_user.id == bot_instance.id
                ):
                    return await handler(event, data)
                if event.caption:
                    message: str = event.caption
                elif event.text:
                    message: str = event.text
                elif hasattr(event, 'message_text'):
                    if event.message_text:
                        message: str = event.message_text
                    else:
                        return
                else:
                    return
                if bot_instance.username in message:
                    return await handler(event, data)
