from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware

from aiogram.types import Message, CallbackQuery
from src.bot.structures.role import Role
from src.db import Database
from src.db.models import User, Chat


class RegisterCheck(BaseMiddleware):
    """
    Middleware будет вызываться каждый раз, когда пользователь будет отправлять боту сообщения (или нажимать
    на кнопку в инлайн-клавиатуре).
    """

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        """ Сама функция для обработки вызова """
        # if event.web_app_data:
        #     return await handler(event, data)

        db: Database = data["db"]
        user = event.from_user
        user_db: User = await db.user.get_by_tg_id(user.id)
        # chat_db: Chat = await db.chat.get_by_where(whereclause=f'self.type_model.chat_id == {event.chat.id}')
        if not user_db:
            chat_model: Chat = Chat(
                chat_id=event.chat.id,
                chat_type=event.chat.type,
                title=event.chat.title,
                chat_name=event.chat.username
            )
            user_model: User = User(
                user_id=user.id,
                user_name=user.username,
                first_name=user.first_name,
                second_name=user.last_name,
                is_premium=user.is_premium,
                role=Role.USER,
                user_chat=chat_model
            )
            db.session.add(user_model)
            await db.session.commit()
        else:
            await db.chat.activity_update(event.from_user.id)

        return await handler(event, data)
