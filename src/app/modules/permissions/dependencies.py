from typing import Annotated

from fastapi import Depends

from app.core.db_session import SessionDEP
from app.modules.permissions.repository import PermissionRepository
from app.modules.permissions.service import PermissionService


def get_permission_repository(session: SessionDEP) -> PermissionRepository:
    return PermissionRepository(session)


def get_permission_service(repo: Annotated[PermissionRepository, Depends(get_permission_repository)]) -> PermissionService:
    return PermissionService(repo)


PermissionServiceDEP = Annotated[PermissionService, Depends(get_permission_service)]
