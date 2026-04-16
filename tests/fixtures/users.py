import uuid

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings
from app.modules.auth.service import hash_password
from app.modules.users.models import UserModel
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
import faker

f = faker.Faker()


@pytest_asyncio.fixture(scope="function")
async def admin_user(
    test_settings: Settings, async_db_session: AsyncSession
) -> UserModel:
    service = UserService(repository=UserRepository(async_db_session))
    existing = await service.get_by_email(test_settings.ADMIN_EMAIL)

    if existing:
        return existing

    user_data = dict(
        email=test_settings.ADMIN_EMAIL,
        phone_number=f.phone_number(),
        password_hash=hash_password(test_settings.ADMIN_PASSWORD.get_secret_value()),
        first_name="Super",
        last_name="Admin",
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )
    await service.repository.create(user_data)
    return await service.get_by_email(test_settings.ADMIN_EMAIL)


@pytest_asyncio.fixture(scope="function")
async def regular_user(
    test_settings: Settings, async_db_session: AsyncSession
) -> UserModel:
    service = UserService(repository=UserRepository(async_db_session))
    unique_id = str(uuid.uuid7())[:8]
    email = f.email()
    user_data = dict(
        email=email,
        phone_number=f.phone_number(),
        password_hash=hash_password("regularpass123"),
        first_name="Regular",
        last_name="User",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    await service.repository.create(user_data)
    return await service.get_by_email(email)
