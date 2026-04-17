from sqlalchemy import select

from app.modules.permissions.models import PermissionModel
from app.modules.permissions.schemas import PermissionSchema
from app.shared.base_repository import RepositoryBase


class PermissionRepository(RepositoryBase[PermissionModel, PermissionSchema]):
    model = PermissionModel
    response_schema = PermissionSchema

    async def get_by_codename(self, codename: str) -> PermissionSchema | None:
        stmt = select(self.model).where(self.model.codename == codename)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is not None:
            return self.response_schema.model_validate(obj)
        return None

    async def exists_by_codename(self, codename: str) -> bool:
        stmt = select(self.model.id).where(self.model.codename == codename)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
