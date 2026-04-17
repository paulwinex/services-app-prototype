from typing import Any
from uuid import UUID

from pydantic import EmailStr

from app.modules.auth import service as auth_service
from app.modules.permissions.models import PermissionModel
from app.modules.users.exceptions import InvalidCredentialsError, UserInactiveError
from app.modules.users.models import UserModel
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreateRequest, UserCreateDB, UserSchema
from app.shared.base_service import ServiceBase
from app.shared.exceptions import ConflictError, NoPermissionError
from app.shared.pagination import PaginationRequest, PaginationResultSchema


class UserService(ServiceBase[UserModel]):
    repository: UserRepository

    async def get_by_email(self, email: str|EmailStr) -> UserSchema | None:
        result = await self.repository.list(
            pagination=PaginationRequest(limit=1),
            filters={"email": str(email)},
        )
        if not result.items:
            return None
        return result.items[0]

    async def get_by_phone_number(self, phone_number: str) -> UserSchema | None:
        result = await self.repository.list(
            pagination=PaginationRequest(limit=1),
            filters={"phone_number": phone_number},
        )
        if not result.items:
            return None
        return result.items[0]

    async def get_super_user(self) -> UserSchema | None:
        return await self.repository.get_super_user()

    async def create_super_user(self, data: SuperUserCreateSchema) -> UserSchema:
        return await self.repository.create_super_user(data)

    async def get_list(
        self, pagination: PaginationRequest, filters: dict[str, Any] | None = None
    ) -> PaginationResultSchema:
        filters = filters or {}
        filters.setdefault("is_active", True)
        return await super().get_list(pagination, filters)

    async def create(self, data: UserCreateRequest | dict) -> UserSchema:
        if isinstance(data, dict):
            data = UserCreateRequest(**data)
        if await self.get_by_email(data.email):
            raise ConflictError(detail=f"User with email {data.email} already exists")
        if await self.get_by_phone_number(data.phone_number):
            raise ConflictError(detail="Phone number already exists")
        data = UserCreateDB(
            **data.model_dump(), password_hash=auth_service.hash_password(data.password)
        )
        return await super().create(data)

    async def authenticate(self, email: str, password: str) -> UserSchema:
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

    async def get_permissions(self, user_id: str | UUID) -> get_list[PermissionModel]:
        return await self.repository.get_user_permissions(user_id)

    async def has_permissions(
        self, user: UserSchema, required_permissions: get_list[str], method=all
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
            raise NoPermissionError(detail="Cannot delete superuser")
        await self.repository.delete(entity_id)
