from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseDBModel, BaseDBUUIDModel
from app.shared.model_mixins import TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.models import UserModel
    from app.modules.permissions.models import PermissionModel


class GroupModel(BaseDBUUIDModel, TimestampMixin):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(2048))
    is_system: Mapped[bool] = mapped_column(default=False, nullable=False)

    user_associations: Mapped[list[UserGroupModel]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
    users: Mapped[list[UserModel]] = relationship(
        secondary="user_groups_m2m",
        back_populates="groups",
        viewonly=True,
    )

    permission_associations: Mapped[list[GroupPermissionModel]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
    permissions: Mapped[list[PermissionModel]] = relationship(
        secondary="group_permissions_m2m",
        back_populates="groups",
        viewonly=True,
    )


class UserGroupModel(BaseDBModel):
    __tablename__ = "user_groups_m2m"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    user: Mapped[UserModel] = relationship(back_populates="group_associations")
    group: Mapped[GroupModel] = relationship(back_populates="user_associations")


class GroupPermissionModel(BaseDBModel):
    __tablename__ = "group_permissions_m2m"

    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    permission_id: Mapped[UUID] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    group: Mapped[GroupModel] = relationship(back_populates="permission_associations")
    permission: Mapped[PermissionModel] = relationship(back_populates="group_associations")
