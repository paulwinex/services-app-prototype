from sqlalchemy import select

from app.modules.permissions.models import PermissionModel
from app.shared.base_repository import RepositoryBase


class PermissionRepository(RepositoryBase):
    model = PermissionModel

    async def get_by_codename(self, codename: str) -> PermissionModel | None:
        stmt = select(self.model).where(self.model.codename == codename)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_codename(self, codename: str) -> bool:
        stmt = select(self.model.id).where(self.model.codename == codename)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
