from typing import Any

from app.modules.permissions.models import PermissionModel
from app.modules.permissions.schemas import PermissionCreateRequest, PermissionUpdateRequest
from app.modules.permissions.repository import PermissionRepository
from app.modules.permissions.exceptions import PermissionAlreadyExistsError
from app.shared.base_service import ServiceBase
from app.shared.pagination import PaginationRequest, PaginationResultSchema


class PermissionService(ServiceBase[PermissionModel]):
    repository: PermissionRepository

    async def get_by_codename(self, codename: str) -> PermissionModel | None:
        result = await self.repository.list(
            pagination=PaginationRequest(limit=1),
            filters={'codename': codename},
        )
        if not result.items:
            return None
        return result.items[0]

    async def create(self, data: PermissionCreateRequest) -> str:
        if isinstance(data, dict):
            data = PermissionCreateRequest.model_validate(data)
        if await self.repository.exists_by_codename(data.codename):
            raise PermissionAlreadyExistsError(f"Permission '{data.codename}' already exists")
        return await self.repository.create(data)

    async def update(self, permission_id: str, data: PermissionUpdateRequest) -> None:
        return await self.repository.update(permission_id, data)
