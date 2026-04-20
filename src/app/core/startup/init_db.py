from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_session import async_session
from app.core.settings import settings
from app.modules.auth.service import hash_password
from app.modules.groups.permissions import GroupPermission
from app.modules.groups.repository import GroupRepository
from app.modules.groups.schemas import GroupCreateAdminRequest
from app.modules.groups.service import GroupService
from app.modules.permissions.permissions import PermissionPermission
from app.modules.permissions.repository import PermissionRepository
from app.modules.permissions.schemas import PermissionCreateRequest
from app.modules.permissions.service import PermissionService
from app.modules.users.permissions import UserPermission
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import SuperUserCreateSchema
from app.modules.users.service import UserService
from app.shared.base_model import BaseDBModel


async def init_database(app: FastAPI):
    async_session.setup()
    await setup_dev_db()  # skip for production
    async with async_session.get_session() as session:
        await _init_superuser(session)
        await _init_permissions(session)
        await _init_system_group(session)
        await _assign_superuser_to_system_group(session)


async def setup_dev_db():
    """Create tables for develop"""
    logger.info("Init database models in dev mode")
    async with async_session.engine.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.create_all)


async def _init_superuser(session: AsyncSession):
    service = UserService(repository=UserRepository(session))
    superuser = await service.get_super_user()
    if superuser:
        return
    user = await service.get_by_email(settings.ADMIN_EMAIL)
    if user:
        logger.info(f"User with email {settings.ADMIN_EMAIL} already exists")
        return

    user_data = SuperUserCreateSchema(
        email=settings.ADMIN_EMAIL,
        password_hash=hash_password(settings.ADMIN_PASSWORD.get_secret_value()),
        phone_number=settings.ADMIN_PHONE_NUMBER,
        first_name="Super",
        last_name="Admin",
        is_superuser=True,
        is_active=True,
        is_verified=True,
    )
    await service.create_super_user(user_data)
    logger.info(f"Created superuser: {settings.ADMIN_EMAIL}")


async def _init_permissions(session: AsyncSession):
    service = PermissionService(repository=PermissionRepository(session))
    all_permissions = (
        list(UserPermission) + list(GroupPermission) + list(PermissionPermission)
    )

    created_count = 0
    for perm in all_permissions:
        existing = await service.get_by_codename(str(perm))
        if existing:
            continue
        perm_data = PermissionCreateRequest(
            name=perm.name.replace("_", " ").title(),
            codename=str(perm),
        )
        await service.create(perm_data)
        created_count += 1

    if created_count:
        logger.info(f"Created {created_count} permissions")
    else:
        logger.info("All permissions already exist")


async def _init_system_group(session: AsyncSession):
    service = GroupService(repository=GroupRepository(session))
    existing = await service.get_by_name("admins")
    if existing:
        logger.info("System group 'admins' already exists")
        return

    group = GroupCreateAdminRequest(
        name="admins",
        description="System administrators with full access",
        is_system=True,
    )
    await service.create(group)
    logger.info("Created system group: admins")


async def _assign_superuser_to_system_group(session: AsyncSession):
    user_service = UserService(repository=UserRepository(session))
    group_service = GroupService(repository=GroupRepository(session))

    superuser = await user_service.get_super_user()
    if not superuser:
        logger.warning("No superuser found to assign to system group")
        return

    admins_group = await group_service.get_by_name("admins")
    if not admins_group:
        logger.warning("System admins group not found")
        return

    if await group_service.user_in_group(superuser.id, admins_group.id):
        logger.info("Superuser already assigned to system admins group")
        return

    await group_service.add_user_to_group(superuser.id, admins_group.id)
    logger.info("Assigned superuser to system admins group")
