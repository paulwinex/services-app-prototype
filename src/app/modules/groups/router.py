from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import has_permissions
from app.modules.groups.dependencies import GroupServiceDEP
from app.modules.groups.permissions import GroupPermission
from app.modules.groups.schemas import (
    GroupCreateRequest,
    GroupUpdateRequest,
    GroupResponse,
    GroupFullResponse,
    GroupListResponse,
    GroupListFilterQuery,
)
from app.shared.pagination import PaginationRequest

router = APIRouter()


@router.get(
    "",
    response_model=GroupListResponse,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_LIST_GROUPS]))],
)
async def list_groups(
    pagination: Annotated[PaginationRequest, Depends()],
    filters: Annotated[GroupListFilterQuery, Depends()],
    service: GroupServiceDEP,
):
    return await service.get_list(pagination, filters.model_dump(exclude_unset=True))


@router.get(
    "/{group_id}",
    response_model=GroupFullResponse,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_VIEW_GROUP]))],
)
async def get_group(group_id: str, service: GroupServiceDEP):
    return await service.get_by_id(group_id)


@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_ADD_GROUP]))],
)
async def create_group(request: GroupCreateRequest, service: GroupServiceDEP):
    return await service.create(request)


@router.patch(
    "/{group_id}",
    response_model=GroupResponse,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_EDIT_GROUP]))],
)
async def update_group(
    group_id: str,
    request: GroupUpdateRequest,
    service: GroupServiceDEP,
):
    return await service.update(group_id, request)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_DELETE_GROUP]))],
)
async def delete_group(group_id: str, service: GroupServiceDEP):
    await service.delete(group_id)


@router.post(
    "/{group_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_MANAGE_GROUP_USERS]))],
)
async def add_user_to_group(group_id: str, user_id: str, service: GroupServiceDEP):
    await service.add_user_to_group(user_id, group_id)


@router.delete(
    "/{group_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_MANAGE_GROUP_USERS]))],
)
async def remove_user_from_group(group_id: str, user_id: str, service: GroupServiceDEP):
    await service.remove_user_from_group(user_id, group_id)


@router.get(
    "/users/{user_id}/groups",
    response_model=GroupListResponse,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_VIEW_GROUP]))],
)
async def list_user_groups(user_id: str, service: GroupServiceDEP):
    return await service.list_user_groups(user_id)
