from datetime import datetime
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field, ConfigDict

from app.shared.pagination import PaginationResultSchema, extra_filter_fields


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str|UUID
    name: str
    codename: str


class PermissionFullResponse(PermissionResponse):
    created_at: datetime
    updated_at: datetime | None = None


class PermissionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    codename: str = Field(..., min_length=1, max_length=100)


class PermissionUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)


@extra_filter_fields(
    in_=("id",),
    gt=("created_at",),
    lt=("created_at",),
    ge=("created_at",),
    le=("created_at",),
    like=("name", "codename"),
)
class PermissionListFilterRequest(BaseModel):
    id: str | None = Query(None, description="Filter by id")
    name: str | None = Query(None, description="Filter by name")
    codename: str | None = Query(None, description="Filter by codename")
    created_at: datetime | None = Query(None, description="Filter by creation time")


class PermissionListResponse(PaginationResultSchema):
    items: list[PermissionResponse]
