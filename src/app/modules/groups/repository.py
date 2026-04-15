from uuid import UUID

from sqlalchemy import select, delete, exists

from app.modules.groups.models import GroupModel, UserGroupModel, GroupPermissionModel
from app.shared.base_repository import RepositoryBase


class GroupRepository(RepositoryBase):
    model = GroupModel

    async def get_by_name(self, name: str) -> GroupModel | None:
        stmt = select(self.model).where(self.model.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_name(self, name: str) -> bool:
        stmt = select(self.model.id).where(self.model.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def user_in_group(self, user_id: str | UUID, group_id: str | UUID) -> bool:
        stmt = select(exists().where(
            UserGroupModel.user_id == user_id,
            UserGroupModel.group_id == group_id,
        ))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_user_groups(self, user_id: str | UUID) -> list[GroupModel]:
        stmt = select(self.model).join(UserGroupModel).where(UserGroupModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_group_users(self, group_id: str | UUID) -> list[UUID]:
        stmt = select(UserGroupModel.user_id).where(UserGroupModel.group_id == group_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def add_user_to_group(self, user_id: str | UUID, group_id: str | UUID) -> None:
        association = UserGroupModel(user_id=user_id, group_id=group_id)
        self.session.add(association)
        await self.session.flush()

    async def remove_user_from_group(self, user_id: str | UUID, group_id: str | UUID) -> None:
        stmt = delete(UserGroupModel).where(
            UserGroupModel.user_id == user_id,
            UserGroupModel.group_id == group_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_group_permissions(self, group_id: str | UUID) -> list[str]:
        stmt = select(GroupPermissionModel.permission_id).where(
            GroupPermissionModel.group_id == group_id
        )
        result = await self.session.execute(stmt)
        return [str(row[0]) for row in result.all()]

    async def add_permission_to_group(self, group_id: str | UUID, permission_id: str | UUID) -> None:
        stmt = select(GroupPermissionModel).where(
            GroupPermissionModel.group_id == group_id,
            GroupPermissionModel.permission_id == permission_id,
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            return
        association = GroupPermissionModel(group_id=group_id, permission_id=permission_id)
        self.session.add(association)
        await self.session.flush()

    async def remove_permission_from_group(self, group_id: str | UUID, permission_id: str | UUID) -> None:
        stmt = delete(GroupPermissionModel).where(
            GroupPermissionModel.group_id == group_id,
            GroupPermissionModel.permission_id == permission_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()
