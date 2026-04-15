from typing import Annotated

from fastapi import Depends

from app.core.db_session import SessionDEP
from app.modules.groups.repository import GroupRepository
from app.modules.groups.service import GroupService


def get_group_repository(session: SessionDEP) -> GroupRepository:
    return GroupRepository(session)


def get_group_service(repo: Annotated[GroupRepository, Depends(get_group_repository)]) -> GroupService:
    return GroupService(repo)


GroupServiceDEP = Annotated[GroupService, Depends(get_group_service)]
