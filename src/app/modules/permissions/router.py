from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import has_permissions
from app.modules.permissions.dependencies import PermissionServiceDEP
from app.modules.permissions.permissions import PermissionPermission
from app.modules.permissions.schemas import (
    PermissionResponse,
    PermissionFullResponse,
    PermissionCreateRequest,
    PermissionUpdateRequest,
    PermissionListResponse,
    PermissionListFilterRequest,
)
from app.shared.pagination import PaginationRequest

router = APIRouter()


@router.get(
    "",
    response_model=PermissionListResponse,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_LIST_PERMISSIONS]))],
)
async def list_permissions(
    pagination: Annotated[PaginationRequest, Depends()],
    filters: Annotated[PermissionListFilterRequest, Depends()],
    service: PermissionServiceDEP,
):
    return await service.list(pagination, filters.model_dump(exclude_unset=True))


@router.get(
    "/{permission_id}",
    response_model=PermissionFullResponse,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_VIEW_PERMISSION]))],
)
async def get_permission(permission_id: str, service: PermissionServiceDEP):
    return await service.get_by_id(permission_id)


@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_ADD_PERMISSION]))],
)
async def create_permission(request: PermissionCreateRequest, service: PermissionServiceDEP):
    permission_id = await service.create(request)
    return await service.get_by_id(permission_id)


@router.patch(
    "/{permission_id}",
    response_model=PermissionResponse,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_EDIT_PERMISSION]))],
)
async def update_permission(
    permission_id: str,
    request: PermissionUpdateRequest,
    service: PermissionServiceDEP,
):
    await service.update(permission_id, request)
    return await service.get_by_id(permission_id)


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_DELETE_PERMISSION]))],
)
async def delete_permission(permission_id: str, service: PermissionServiceDEP):
    await service.delete(permission_id)
