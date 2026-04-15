from uuid import uuid7

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseDBModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id}>"

    __str__ = __repr__


class BaseDBUUIDModel(BaseDBModel):
    __abstract__ = True
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
