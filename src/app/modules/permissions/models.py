from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseDBUUIDModel
from app.shared.model_mixins import TimestampMixin

if TYPE_CHECKING:
    from app.modules.groups.models import GroupModel, GroupPermissionModel


class PermissionModel(BaseDBUUIDModel, TimestampMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    codename: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)

    group_associations: Mapped[list[GroupPermissionModel]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    groups: Mapped[list[GroupModel]] = relationship(
        secondary="group_permissions_m2m",
        back_populates="permissions",
        viewonly=True,
    )
