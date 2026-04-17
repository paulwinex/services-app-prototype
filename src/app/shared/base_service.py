from abc import ABC
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.shared.base_repository import RepositoryBase
from app.shared.pagination import PaginationResultSchema, PaginationRequest
from app.shared.type_aliases import TSchema


class ServiceBase[TSchema](ABC):
    repository: RepositoryBase

    def __init__(self, repository: RepositoryBase):
        self.repository = repository

    async def get_by_id(self, entity_id: str|UUID) -> TSchema:
        return await self.repository.get_by_id(entity_id)

    async def create(self, data: dict|BaseModel) -> TSchema:
        return await self.repository.create(data)

    async def update(self, entity_id: str|UUID, data: dict|BaseModel) -> TSchema:
        return await self.repository.update(entity_id, data)

    async def delete(self, entity_id: str|UUID) -> None:
        await self.repository.delete(entity_id)

    async def get_list(self, pagination: PaginationRequest, filters: dict[str, Any] | None = None) -> PaginationResultSchema:
        return await self.repository.list(pagination, filters)
