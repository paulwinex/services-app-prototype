from datetime import datetime
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field, ConfigDict

from app.shared.pagination import PaginationResultSchema, extra_filter_fields


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str|UUID
    name: str
    description: str | None = None
    is_system: bool


class GroupFullResponse(GroupResponse):
    created_at: datetime
    updated_at: datetime | None = None


class GroupCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    description: str | None = Field(None, max_length=2048)


class GroupUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=32)
    description: str | None = Field(None, max_length=2048)


@extra_filter_fields(
    in_=("id",),
    gt=("created_at",),
    lt=("created_at",),
    ge=("created_at",),
    le=("created_at",),
    like=("name", "description"),
)
class GroupListFilterRequest(BaseModel):
    id: str | None = Query(None, description="Filter by id")
    name: str | None = Query(None, description="Filter by name")
    description: str | None = Query(None, description="Filter by description")
    is_system: bool | None = Query(None, description="Filter by system flag")
    created_at: datetime | None = Query(None, description="Filter by creation time")


class GroupListResponse(PaginationResultSchema):
    items: list[GroupResponse]
