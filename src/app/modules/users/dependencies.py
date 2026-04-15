from typing import Annotated

from fastapi import Depends

from app.core.db_session import SessionDEP
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService


def get_user_repository(session: SessionDEP) -> UserRepository:
    return UserRepository(session)


def get_user_service(repo: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    return UserService(repo)


UserServiceDEP = Annotated[UserService, Depends(get_user_service)]
