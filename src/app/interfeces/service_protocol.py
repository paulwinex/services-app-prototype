from typing import Protocol
from uuid import UUID

from app.interfeces.type_aliases import TModel
from app.shared.pagination import PaginationRequest, PaginationResultSchema


class ServiceProtocol(Protocol):
    async def get_by_id(self, entity_id: str|UUID) -> TModel: ...

    async def create(self, entity: TModel) -> str|UUID: ...

    async def update(self, entity_id: str|UUID, **kwargs) -> None: ...

    async def delete(self, entity_id: str|UUID) -> None: ...

    async def list(self, pagination: PaginationRequest | None = None, filters: dict | None = None) -> PaginationResultSchema: ...
