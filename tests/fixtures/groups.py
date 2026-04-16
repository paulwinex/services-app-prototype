import uuid

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import UserModel
from app.modules.groups.models import GroupModel, UserGroupModel, GroupPermissionModel
from app.modules.permissions.models import PermissionModel
from app.modules.groups.repository import GroupRepository
from app.modules.groups.service import GroupService
from app.modules.permissions.repository import PermissionRepository
from app.modules.permissions.service import PermissionService


@pytest_asyncio.fixture(scope="function")
async def test_group(async_db_session: AsyncSession) -> GroupModel:
    service = GroupService(repository=GroupRepository(async_db_session))
    unique_id = str(uuid.uuid4())[:8]
    group = GroupModel(
        id=str(uuid.uuid7()),
        name=f"Test Group {unique_id}",
        description="Test group for testing",
        is_system=False,
    )
    await service.repository.create(group)
    return await service.get_by_name(f"Test Group {unique_id}")


@pytest_asyncio.fixture(scope="function")
async def system_group(async_db_session: AsyncSession) -> GroupModel:
    service = GroupService(repository=GroupRepository(async_db_session))
    existing = await service.get_by_name("admins")

    if existing:
        return existing

    group = GroupModel(
        id=str(uuid.uuid7()),
        name="admins",
        description="System administrators",
        is_system=True,
    )
    await service.repository.create(group)
    return await service.get_by_name("admins")


@pytest_asyncio.fixture(scope="function")
async def test_permission(async_db_session: AsyncSession) -> PermissionModel:
    service = PermissionService(repository=PermissionRepository(async_db_session))
    unique_id = str(uuid.uuid4())[:8]
    permission = PermissionModel(
        id=str(uuid.uuid4()),
        name=f"Test Permission {unique_id}",
        codename=f"test.can_test_{unique_id}",
    )
    await service.repository.create(permission)
    return await service.get_by_codename(f"test.can_test_{unique_id}")


@pytest_asyncio.fixture(scope="function")
async def group_with_permissions(
    async_db_session: AsyncSession, test_permission: PermissionModel
) -> GroupModel:
    group_service = GroupService(repository=GroupRepository(async_db_session))
    unique_id = str(uuid.uuid7())[:8]
    group = GroupModel(
        id=str(uuid.uuid7()),
        name=f"Group With Permissions {unique_id}",
        description="Test group with permissions",
        is_system=False,
    )
    await group_service.repository.create(group)
    group = await group_service.get_by_name(f"Group With Permissions {unique_id}")
    await group_service.add_permission_to_group(group.id, test_permission.id)
    return group


@pytest_asyncio.fixture(scope="function")
async def user_in_group(
    async_db_session: AsyncSession, regular_user: UserModel, test_group: GroupModel
):
    service = GroupService(repository=GroupRepository(async_db_session))
    await service.add_user_to_group(regular_user.id, test_group.id)
    return regular_user
