from enum import StrEnum
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.modules.auth.service import AuthService
from app.modules.groups.dependencies import GroupServiceDEP
from app.modules.users.dependencies import UserServiceDEP
from app.modules.users.schemas import UserResponse
from app.shared.exceptions import ForbiddenError, NotFoundError
from app.shared.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(user_service: UserServiceDEP) -> AuthService:
    return AuthService(user_service)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    if not token:
        raise UnauthorizedError()
    user = await service.get_current_user(token)
    if not user:
        raise NotFoundError
    return UserResponse.model_validate(user)


async def get_active_user(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not user.is_active:
        raise UnauthorizedError()
    return user


def has_permissions(required_permissions: list[StrEnum]):
    # create checker function for route
    async def permission_checker(
        user: UserResponse = Depends(CurrentUserDEP),
        group_service = Depends(GroupServiceDEP),
    ) -> None:
        if not required_permissions or user.is_superuser:
            return
        user_groups = await group_service.get_user_groups(user.id)
        group_ids = [g.id for g in user_groups]
        user_permission_codenames = set()
        for group_id in group_ids:
            perms = await group_service.repository.get_group_permissions(group_id)
            user_permission_codenames.update(perms)
        for perm in required_permissions:
            if str(perm) not in user_permission_codenames:
                raise ForbiddenError(f"Permission {perm} required")

    return permission_checker


CurrentUserDEP = Annotated[UserResponse, Depends(get_current_user)]
ActiveUserDEP = Annotated[UserResponse, Depends(get_active_user)]
AuthServiceDEP = Annotated[AuthService, Depends(get_auth_service)]
LoginDataDEP = Annotated[OAuth2PasswordRequestForm, Depends()]
