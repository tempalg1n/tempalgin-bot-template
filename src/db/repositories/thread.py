"""Thread repository file."""
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..models.thread import ThreadModel
from .abstract import Repository


class ThreadRepo(Repository[ThreadModel]):
    """Thread repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(type_model=ThreadModel, session=session)

    async def new(
        self,
        thread_id: str = None,
        user: User = None,
        tag: str = None,
    ) -> ThreadModel:
        """Insert a new object into the database."""
        model = ThreadModel(
            thread_id=thread_id,
            user=user,
            tag=tag,
        )
        return await self.session.merge(model)

    async def get_by_id(self, id_: str) -> ThreadModel:
        stmt = select(ThreadModel).where(ThreadModel.thread_id == id_)
        return await self.session.scalar(stmt)

    async def get_user_threads(self, user_pk: int) -> list[ThreadModel]:
        stmt = select(ThreadModel).where(ThreadModel.user_chat == user_pk)
        return [item for item in await self.session.scalars(stmt)]

    async def deactivate(self, thread_id: str):
        stmt = (
            update(ThreadModel)
            .where(ThreadModel.thread_id == thread_id)
            .values({'is_active': False})
        )
        await self.session.execute(stmt)

    async def get_all_with(
        self, owner_fk: int = None, visible: bool = None
    ) -> list[ThreadModel]:
        stmt = select(ThreadModel)
        if owner_fk:
            stmt = stmt.where(ThreadModel.user_chat_fk == owner_fk)
        if visible is not None:
            stmt = stmt.where(ThreadModel.visible.is_(visible))
        else:
            stmt = stmt.order_by(
                ThreadModel.visible, ThreadModel.created_at.desc()
            )
        return [item for item in await self.session.scalars(stmt)]

    async def delete(
        self, pk: int | None = None, thread_id: str | None = None
    ):
        stmt = delete(ThreadModel)
        if pk:
            stmt = stmt.where(ThreadModel.id == pk)
        elif thread_id:
            stmt = stmt.where(ThreadModel.thread_id == thread_id)
        else:
            return
        await self.session.execute(stmt)