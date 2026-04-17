from uuid import UUID

from sqlalchemy import select

from app.modules.groups.models import GroupPermissionModel, UserGroupModel
from app.modules.permissions.models import PermissionModel
from app.modules.permissions.schemas import PermissionSchema
from app.modules.users.models import UserModel
from app.modules.users.schemas import UserSchema
from app.shared.base_repository import RepositoryBase


class UserRepository(RepositoryBase):
    model = UserModel
    response_schema = UserSchema

    async def get_by_email(self, email: str) -> UserSchema | None:
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        return self.response_schema.model_validate(result.scalar_one_or_none())

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_super_user(self) -> UserSchema | None:
        stmt = select(UserModel).where(UserModel.is_superuser == True)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is not None:
            return self.response_schema.model_validate(obj)
        return None

    async def get_user_permissions(self, user_id: str | UUID) -> list[PermissionSchema]:
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        stmt = (
            select(PermissionModel)
            .join(
                GroupPermissionModel,
                GroupPermissionModel.permission_id == PermissionModel.id,
            )
            .join(
                UserGroupModel, UserGroupModel.group_id == GroupPermissionModel.group_id
            )
            .where(UserGroupModel.user_id == user_uuid)
            .distinct()
        )
        result = await self.session.execute(stmt)
        return [PermissionSchema.model_validate(x) for x in result.scalars().all()]
