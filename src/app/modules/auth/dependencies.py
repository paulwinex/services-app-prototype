from typing import Annotated, Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.modules.auth.service import AuthService
from app.modules.users.dependencies import UserServiceDEP
from app.modules.users.schemas import UserResponse, UserFull
from app.shared.exceptions import NotFoundError, NoPermissionError
from app.shared.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(user_service: UserServiceDEP) -> AuthService:
    return AuthService(user_service)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserFull:
    if not token:
        raise UnauthorizedError()
    user = await service.get_user_by_token(token)
    if not user:
        raise NotFoundError
    return UserFull.model_validate(user)


async def get_active_user(user: UserFull = Depends(get_current_user)) -> UserFull:
    if not user.is_active:
        raise UnauthorizedError()
    return user


def has_permissions(required_permissions: list, method: Callable|None = None) -> Callable:
    if not required_permissions:
        raise ValueError("Required permissions are empty")

    async def dependency(
        user_service: UserServiceDEP,
        user: UserFull = Depends(get_current_user),
    ):
        permission_list = tuple(str(p) for p in required_permissions)
        if user.is_superuser:
            return
        if not (await user_service.has_permissions(user, permission_list, method=method or all)):
            raise NoPermissionError(
                detail=f"You have no permissions for this action: {permission_list}"
            )

    return dependency


CurrentUserDEP = Annotated[UserResponse, Depends(get_current_user)]
ActiveUserDEP = Annotated[UserResponse, Depends(get_active_user)]
AuthServiceDEP = Annotated[AuthService, Depends(get_auth_service)]
LoginDataDEP = Annotated[OAuth2PasswordRequestForm, Depends()]
