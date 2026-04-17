from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import has_permissions
from app.modules.users.dependencies import UserServiceDEP
from app.modules.users.permissions import UserPermission
from app.modules.users.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserSchema,
    UserListResponse,
    UserListFilterRequest,
    UserPasswordChangeRequest,
)
from app.shared.pagination import PaginationRequest

router = APIRouter()


@router.get(
    "",
    response_model=UserListResponse,
    dependencies=[Depends(has_permissions([UserPermission.CAN_LIST_USERS]))],
)
async def list_users(
    pagination: Annotated[PaginationRequest, Depends()],
    filters: Annotated[UserListFilterRequest, Depends()],
    service: UserServiceDEP,
):
    return await service.get_list(pagination, filters.model_dump(exclude_unset=True))


@router.post(
    "/{user_id}/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([UserPermission.CAN_EDIT_USER]))],
)
async def change_user_password(
    user_id: str, payload: UserPasswordChangeRequest, service: UserServiceDEP
):
    await service.change_password(
        user_id, payload.current_password, payload.new_password
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(has_permissions([UserPermission.CAN_VIEW_USER]))],
)
async def get_user(user_id: str, service: UserServiceDEP):
    return await service.get_by_id(user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permissions([UserPermission.CAN_ADD_USER]))],
)
async def create_user(request: UserCreateRequest, service: UserServiceDEP):
    return await service.create(request)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(has_permissions([UserPermission.CAN_EDIT_USER]))],
)
async def update_user(
    user_id: str, payload: UserUpdateRequest, service: UserServiceDEP
):
    return await service.update(user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([UserPermission.CAN_DELETE_USER]))],
)
async def delete_user(user_id: str, service: UserServiceDEP):
    await service.delete(user_id)
