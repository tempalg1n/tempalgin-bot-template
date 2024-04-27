import logging
from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.types import User as TelegramUser
from sqlalchemy import Row

from src.bot.structures.role import Role
from src.db import Database
from src.db.models import Chat, User

logger = logging.getLogger(__name__)


class RegisterCheck(BaseMiddleware):
    """
    Middleware будет вызываться каждый раз, когда пользователь будет отправлять боту сообщения (или нажимать
    на кнопку в инлайн-клавиатуре).
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        """Сама функция для обработки вызова"""
        db: Database = data['db']
        tg_user: TelegramUser = event.from_user
        user: Row = await db.user.get_by_where(User.user_id == tg_user.id)
        if user:
            data['user'] = user[0]
            logger.debug('User from database injected')
        else:
            logger.info('User not found. Creating new, but first getting chat from db...')
            chat: Chat | None = await db.chat.get_by_where(Chat.chat_id == event.chat.id)
            if not chat:
                chat: Chat = await db.chat.new(
                    chat_id=event.chat.id,
                    chat_type=event.chat.type,
                    title=event.chat.title,
                    chat_name=event.chat.username if event.chat.username else 'unknown_chat',
                )
                logger.info('Chat not found. New chat added to session')
            user: User = await db.user.new(
                user_id=tg_user.id,
                user_name=tg_user.username,
                first_name=tg_user.first_name,
                language_code=tg_user.language_code,
                second_name=tg_user.last_name,
                is_premium=tg_user.is_premium,
                role=Role.USER,
                user_chat=chat,
            )
            logger.info('New user added to session')
            await db.session.commit()
            logger.info('New user created')

        return await handler(event, data)
