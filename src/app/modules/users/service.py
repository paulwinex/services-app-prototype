from typing import Any
from uuid import UUID

from app.modules.auth import service as auth_service
from app.modules.permissions.models import PermissionModel
from app.modules.users.exceptions import InvalidCredentialsError, UserInactiveError
from app.modules.users.models import UserModel
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreateRequest, UserCreateDB, UserFull
from app.shared.base_service import ServiceBase
from app.shared.pagination import PaginationRequest, PaginationResultSchema


class UserService(ServiceBase[UserModel]):
    repository: UserRepository

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.repository.list(
            pagination=PaginationRequest(limit=1),
            filters={"email": email},
        )
        if not result.items:
            return None
        return result.items[0]

    async def create(self, data: UserCreateRequest | dict) -> str:
        if isinstance(data, dict):
            data = UserCreateRequest(**data)
        data = UserCreateDB(
            **data.model_dump(), password_hash=auth_service.hash_password(data.password)
        )
        return await super().create(data)

    async def list(
        self, pagination: PaginationRequest, filters: dict[str, Any] | None = None
    ) -> PaginationResultSchema:
        filters = filters or {}
        filters.setdefault("is_active", True)
        return await super().list(pagination, filters)

    async def authenticate(self, email: str, password: str) -> UserModel:
        user = await self.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()
        if not auth_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise UserInactiveError()
        return user

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> None:
        user = await self.repository.get_by_id(user_id)
        if user.is_superuser:
            from app.shared.exceptions import NoPermissionError

            raise NoPermissionError(detail="Cannot change superuser password")
        if not auth_service.verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()
        await self.repository.update(
            user_id, dict(password_hash=auth_service.hash_password(new_password))
        )

    async def get_permissions(self, user_id: str | UUID) -> list[PermissionModel]:
        return await self.repository.get_user_permissions(user_id)

    async def has_permissions(
        self, user: UserFull, required_permissions: list[str], method=all
    ) -> bool:
        permissions = await self.get_permissions(user.id)
        permission_codenames = {perm.codename for perm in permissions}
        required_set = set(required_permissions)
        if method is all:
            return required_set.issubset(permission_codenames)
        else:
            return bool(required_set & permission_codenames)

    async def delete(self, entity_id: str | UUID) -> None:
        entity = await self.repository.get_by_id(entity_id)
        if entity.is_superuser:
            from app.shared.exceptions import NoPermissionError

            raise NoPermissionError(detail="Cannot delete superuser")
        await self.repository.delete(entity_id)
