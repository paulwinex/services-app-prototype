from typing import Any
from uuid import UUID

from app.modules.groups.models import GroupModel
from app.modules.groups.schemas import (
    GroupCreateRequest,
    GroupUpdateRequest,
    GroupListResponse,
)
from app.modules.groups.repository import GroupRepository
from app.modules.groups.exceptions import (
    GroupAlreadyExistsError,
    SuperUserGroupError,
    UserAlreadyInGroupError,
    UserNotInGroupError,
)
from app.shared.base_service import ServiceBase
from app.shared.pagination import PaginationRequest, PaginationResultSchema


class GroupService(ServiceBase[GroupModel]):
    repository: GroupRepository

    async def get_by_name(self, name: str) -> GroupModel | None:
        result = await self.repository.list(
            pagination=PaginationRequest(limit=1),
            filters={"name": name},
        )
        if not result.items:
            return None
        return result.items[0]

    async def get_list(
        self, pagination: PaginationRequest, filters: dict[str, Any] | None = None
    ) -> PaginationResultSchema:
        return await super().get_list(pagination, filters)

    async def create(self, data: GroupCreateRequest) -> str:
        if await self.repository.exists_by_name(data.name):
            raise GroupAlreadyExistsError(f"Group '{data.name}' already exists")
        return await self.repository.create(data)

    async def update(self, group_id: str | UUID, data: GroupUpdateRequest) -> GroupModel:
        group = await self.repository.get_by_id(group_id)
        if data.name and data.name != group.name:
            if await self.repository.exists_by_name(data.name):
                raise GroupAlreadyExistsError(f"Group '{data.name}' already exists")
        return await self.repository.update(group_id, data)

    async def delete(self, group_id: str | UUID) -> None:
        group = await self.repository.get_by_id(group_id)
        if group.is_system:
            raise SuperUserGroupError("Cannot delete system group")
        await self.repository.delete(group_id)

    async def add_user_to_group(
        self, user_id: str | UUID, group_id: str | UUID
    ) -> None:
        if await self.repository.user_in_group(user_id, group_id):
            raise UserAlreadyInGroupError(f"User {user_id} already in group {group_id}")
        await self.repository.add_user_to_group(user_id, group_id)

    async def remove_user_from_group(
        self, user_id: str | UUID, group_id: str | UUID
    ) -> None:
        if not await self.repository.user_in_group(user_id, group_id):
            raise UserNotInGroupError(f"User {user_id} not in group {group_id}")
        # TODO disable edit super admin
        await self.repository.remove_user_from_group(user_id, group_id)

    async def get_user_groups(self, user_id: str | UUID) -> get_list[GroupModel]:
        return await self.repository.get_user_groups(user_id)

    async def list_user_groups(self, user_id: str | UUID) -> GroupListResponse:
        return await self.repository.get_user_groups(user_id)

    async def add_permission_to_group(
        self, group_id: str | UUID, permission_id: str | UUID
    ) -> None:
        await self.repository.add_permission_to_group(group_id, permission_id)

    async def remove_permission_from_group(
        self, group_id: str | UUID, permission_id: str | UUID
    ) -> None:
        await self.repository.remove_permission_from_group(group_id, permission_id)
