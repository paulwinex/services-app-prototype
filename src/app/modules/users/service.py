from typing import Any

from app.modules.auth.service import hash_password, verify_password
from app.modules.users.exceptions import InvalidCredentialsError, UserInactiveError
from app.modules.users.models import UserModel
from app.shared.base_service import ServiceBase
from app.shared.pagination import PaginationRequest, PaginationResultSchema


class UserService(ServiceBase[UserModel]):
    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.repository.list(
            pagination=PaginationRequest(limit=1),
            filters={'email': email},
        )
        if not result.items:
            return None
        return result.items[0]

    async def list(self, pagination: PaginationRequest, filters: dict[str, Any] | None = None) -> PaginationResultSchema:
        filters = filters or {}
        filters.setdefault('is_active', True)
        return await super().list(pagination, filters)

    async def authenticate(self, email: str, password: str) -> UserModel:
        user = await self.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise UserInactiveError()
        return user

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        user = await self.get_by_id(user_id)
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()
        await self.repository.update(user_id, password_hash=hash_password(new_password))
