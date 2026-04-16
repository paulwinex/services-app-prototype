from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, func, update, delete, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.utils import utcnow
from app.shared.exceptions import NotFoundError, RequestValueError
from app.shared.model_mixins import SoftDeleteMixin
from app.shared.pagination import PaginationResultSchema, PaginationRequest


class RepositoryBase[TModel]:
    model: type[TModel]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, entity_id: str|UUID) -> TModel:
        entity = await self.session.get(self.model, entity_id)
        if not entity:
            raise NotFoundError(detail=f"{self.model.__name__} with id {entity_id} not found")
        return entity

    async def create(self, entity: TModel|dict) -> str:
        if isinstance(entity, dict):
            entity = self.model(**entity)
        elif isinstance(entity, BaseModel):
            entity = self.model(**entity.model_dump(exclude_unset=True))
        self.session.add(entity)
        await self.session.flush([entity])
        return entity.id

    async def update(self, entity_id: str, data: dict|TModel) -> None:
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True)
        stmt = (
            update(self.model)
            .where(self.model.id == entity_id)
            .values(**data)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def list(
        self,
        pagination: PaginationRequest | None = None,
        filters: dict[str, Any] | None = None,
    ) -> PaginationResultSchema:
        if pagination is None:
            pagination = PaginationRequest()
        filters = {k: v for k, v in filters.items() if v is not None}
        total = await self._count_query(filters)
        stmt = select(self.model)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_ordering(stmt, pagination)
        if pagination.offset:
            stmt = stmt.offset(pagination.offset)
        stmt = stmt.limit(pagination.limit)
        result = await self.session.execute(stmt)
        models = list(result.scalars().all())
        return PaginationResultSchema(
            total=total,
            offset=pagination.offset,
            limit=pagination.limit,
            items=models,
            order_by=pagination.order_by,
            sorting=pagination.sorting,
        )

    async def _count_query(self, filters: dict[str, Any] | None = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply_filters(stmt, filters)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0
    
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        return await self._count_query(filters)

    async def exists(self, entity_id: str|UUID) -> bool:
        try:
            await self.get_by_id(entity_id)
            return True
        except NotFoundError:
            return False
        
    async def delete(self, entity_id: str | UUID) -> None:
        if SoftDeleteMixin in self.model.mro():
            await self.update(entity_id, dict(deleted_at=utcnow()))
        else:
            stmt = delete(self.model).where(self.model.id == entity_id)
            await self.session.execute(stmt)
            await self.session.flush()
        
    def _apply_filters(self, stmt: Select, filters: dict[str, Any] | None) -> Select:
        if not filters or not self.model:
            return stmt

        if SoftDeleteMixin in self.model.mro():
            # skip deleted
            stmt = stmt.where(self.model.deleted_at.is_(None))

        for key, value in filters.items():
            if "__" in key:
                field, operator = key.split("__")
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    if operator == "in":
                        stmt = stmt.filter(field_attr.in_(value))
                    elif operator == "not_in":
                        stmt = stmt.filter(~field_attr.in_(value))
                    elif operator == "is_null":
                        stmt = stmt.filter(field_attr.is_(None) if value else field_attr.isnot(None))
                    elif operator == "is_not_null":
                        stmt = stmt.filter(field_attr.isnot(None) if value else field_attr.is_(None))
                    elif operator in ["gt", "lt", "ge", "le"]:
                        stmt = stmt.filter(getattr(field_attr, f"__{operator}__")(value))
                    elif operator == "like":
                        stmt = stmt.filter(field_attr.like(f"%{value}%"))
                    else:
                        raise RequestValueError(detail=f"Unsupported filter operator: {operator}")
                else:
                    raise RequestValueError(detail=f"Invalid filter field: {field}")
            else:
                if hasattr(self.model, key):
                    stmt = stmt.filter(getattr(self.model, key) == value)
        return stmt

    def _apply_ordering(self, stmt: Select, pagination: PaginationRequest) -> Select:
        order_field = pagination.order_by or "id"
        order_column = getattr(self.model, order_field, None)
        if not order_column:
            raise RequestValueError(f'Field {order_column} is invalid for model {self.model.__name__}')
        return stmt.order_by(order_column.desc() if pagination.is_desc else order_column.asc())

