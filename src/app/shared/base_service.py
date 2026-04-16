from abc import ABC
from typing import Any
from uuid import UUID

from app.shared.base_repository import RepositoryBase
from app.shared.pagination import PaginationResultSchema, PaginationRequest
from app.shared.type_aliases import TSchema


class ServiceBase[TModel](ABC):
    repository: RepositoryBase[TModel]

    def __init__(self, repository: RepositoryBase[TModel]):
        self.repository = repository

    async def get_by_id(self, entity_id: str|UUID) -> TModel:
        return await self.repository.get_by_id(entity_id)

    async def create(self, data: dict|TSchema) -> TModel:
        return await self.repository.create(data)

    async def update(self, entity_id: str|UUID, data: TSchema) -> TModel:
        return await self.repository.update(entity_id, data)

    async def delete(self, entity_id: str|UUID) -> None:
        await self.repository.delete(entity_id)

    async def get_list(self, pagination: PaginationRequest, filters: dict[str, Any] | None = None) -> PaginationResultSchema:
        return await self.repository.list(pagination, filters)
