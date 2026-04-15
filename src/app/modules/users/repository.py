from sqlalchemy import select

from app.modules.users.models import UserModel
from app.shared.base_repository import RepositoryBase


class UserRepository(RepositoryBase):
    model = UserModel

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_super_user(self) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.is_superuser == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
