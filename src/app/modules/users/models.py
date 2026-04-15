from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseDBUUIDModel
from app.shared.model_mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.modules.groups.models import GroupModel, UserGroupModel


class UserModel(BaseDBUUIDModel, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    phone_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(256), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    group_associations: Mapped[list[UserGroupModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    groups: Mapped[list[GroupModel]] = relationship(
        secondary="user_groups_m2m",
        back_populates="users",
        viewonly=True,
    )

    def __str__(self) -> str:
        return f"User({self.email})"

    def __repr__(self) -> str:
        return f"<User({self.email})>"
