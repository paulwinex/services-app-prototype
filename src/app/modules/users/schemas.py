from datetime import datetime
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.core.events.schemas import BaseEvent
from app.shared.pagination import PaginationResultSchema, extra_filter_fields


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str|UUID
    email: str
    phone_number: str
    first_name: str | None = None
    last_name: str | None = None


class UserSchema(UserResponse):
    password_hash: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
    is_active: bool
    is_verified: bool
    is_superuser: bool


class UserCreateRequest(BaseModel):
    email: EmailStr
    phone_number: str
    password: str
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    is_active: bool = True  # TODO set to false later


class UserCreateDB(BaseModel):
    email: EmailStr
    phone_number: str
    password_hash: str
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class SuperUserCreateSchema(BaseModel):
    email: EmailStr
    phone_number: str
    password_hash: str
    first_name: str
    last_name: str
    is_active: bool = True
    is_verified: bool = True
    is_superuser: bool = True


class UserUpdateRequest(BaseModel):
    email: str | None = None
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
    like=("first_name", "last_name", "phone_number"),
)
class UserListFilterRequest(BaseModel):
    id: str|None = Query(None, description="Filter by id")
    email: str|None = Query(None, description="Filter by email")
    phone_number: str|None = Query(None, description="Filter by phone number")
    is_active: bool|None = Query(None, description="Filter by active flag")
    first_name: str|None = Query(None, description="Filter by first name")
    last_name: str|None = Query(None, description="Filter by last name")
    created_at: datetime|None = Query(None, description="Filter by creation time")


class UserListResponse(PaginationResultSchema):
    items: list[UserResponse]


class UserEvent(BaseEvent):
    id: str|UUID
