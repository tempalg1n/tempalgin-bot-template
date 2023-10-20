"""Chat repository file."""
from sqlalchemy import update, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Chat
from ..models import User as _User
from .abstract import Repository


class ChatRepo(Repository[Chat]):
    """Chat repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize chat repository as for all chats or only for one chat."""
        super().__init__(type_model=Chat, session=session)

    async def new(
        self,
        chat_id: int,
        chat_type: str,
        title: str,
        chat_name: str,
        chat_user: _User,
    ) -> None:
        """Insert a new user into the database."""
        new_chat = await self.session.merge(
            Chat(
                chat_id=chat_id,
                chat_type=chat_type,
                title=title,
                chat_name=chat_name,
                chat_user=chat_user,
            )
        )
        return new_chat

    async def activity_update(self, chat_id: int):
        stmt = update(Chat).where(Chat.chat_id == chat_id).values(last_activity=func.now())
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_private_chats(self):
        stmt = select(Chat.chat_id).where(Chat.chat_type == 'private')
        return await self.session.scalars(stmt)
