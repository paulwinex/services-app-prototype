from datetime import datetime

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.shared.pagination import PaginationResultSchema, extra_filter_fields


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None


class UserFullResponse(UserResponse):
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
    is_active: bool
    is_verified: bool


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class UserPasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


@extra_filter_fields(
    in_=("id",),
    gt=("created_at",),
    lt=("created_at",),
    ge=("created_at",),
    le=("created_at",),
    like=("first_name", "last_name"),
)
class UserListFilterRequest(BaseModel):
    email: str|None = Query(None, description="Filter by email")
    is_active: bool|None = Query(None, description="Filter by active flag")
    first_name: str|None = Query(None, description="Filter by first name")
    last_name: str|None = Query(None, description="Filter by last name")
    created_at: datetime|None = Query(None, description="Filter by creation time")


class UserListResponse(PaginationResultSchema):
    items: list[UserResponse]
