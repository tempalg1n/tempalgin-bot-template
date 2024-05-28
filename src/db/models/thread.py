"""Thread model file."""
import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, func, orm
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ThreadModel(Base):
    """Thread model."""

    thread_id: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=False
    )
    user_fk: Mapped[int] = mapped_column(
        sa.ForeignKey('user.id'), unique=False, nullable=False
    )
    user: Mapped['User'] = orm.relationship(
        'User', uselist=False, lazy='selectin', foreign_keys=user_fk
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
