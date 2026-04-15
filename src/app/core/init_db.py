from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_session import async_session
from app.core.settings import get_settings
from app.modules.auth.service import hash_password
from app.modules.groups.models import GroupModel, UserGroupModel
from app.modules.groups.permissions import GroupPermission
from app.modules.permissions.models import PermissionModel
from app.modules.permissions.permissions import PermissionPermission
from app.modules.users.models import UserModel
from app.modules.users.permissions import UserPermission
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
from app.shared.base_model import BaseDBModel


async def init_database():
    await setup_dev_db() # skip for production
    async with async_session.get_session() as session:
        await _init_superuser(session)
        # await _init_permissions(session)
        # await _init_system_group(session)
        # await _assign_superuser_to_system_group(session)

async def setup_dev_db():
    """Create tables for develop"""
    logger.info("Init database models in dev mode")
    async with async_session.engine.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.create_all)


async def _init_superuser(session: AsyncSession):
    service = UserService(repository=UserRepository(session))
    settings = get_settings()
    superuser = await service.repository.get_super_user()
    if superuser:
        return
    user = await service.get_by_email(settings.ADMIN_EMAIL)
    if user:
        logger.info(f"User with email {settings.ADMIN_EMAIL} already exists")
        return

    password_hash = hash_password(settings.ADMIN_PASSWORD.get_secret_value())

    user_data = dict(
        email=settings.ADMIN_EMAIL,
        password_hash=password_hash,
        first_name="Super",
        last_name="Admin",
        is_superuser=True,
        is_active=True,
        is_verified=True,
    )
    await service.create(user_data)
    logger.info(f"Created superuser: {settings.ADMIN_EMAIL}")


async def _init_permissions(session: AsyncSession):
    all_permissions = list(UserPermission) + list(GroupPermission) + list(PermissionPermission)

    stmt = select(PermissionModel.codename)
    result = await session.execute(stmt)
    existing_codenames = {row[0] for row in result.all()}

    permissions_to_create = [
        PermissionModel(
            name=perm.name.replace("_", " ").title(),
            codename=str(perm),
        )
        for perm in all_permissions
        if str(perm) not in existing_codenames
    ]

    if permissions_to_create:
        session.add_all(permissions_to_create)
        await session.flush()
        logger.info(f"Created {len(permissions_to_create)} permissions")
    else:
        logger.info("All permissions already exist")


async def _init_system_group(session: AsyncSession):
    stmt = select(GroupModel).where(GroupModel.name == "admins")
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        logger.info("System group 'admins' already exists")
        return

    group = GroupModel(
        name="admins",
        description="System administrators with full access",
        is_system=True,
    )
    session.add(group)
    await session.flush()
    logger.info("Created system group: admins")


async def _assign_superuser_to_system_group(session: AsyncSession):
    stmt = select(UserModel).where(UserModel.is_superuser == True)
    result = await session.execute(stmt)
    superuser = result.scalar_one_or_none()

    if not superuser:
        logger.warning("No superuser found to assign to system group")
        return

    stmt = select(GroupModel).where(GroupModel.name == "admins", GroupModel.is_system == True)
    result = await session.execute(stmt)
    admins_group = result.scalar_one_or_none()

    if not admins_group:
        logger.warning("System admins group not found")
        return

    stmt = select(UserGroupModel).where(
        UserGroupModel.user_id == superuser.id,
        UserGroupModel.group_id == admins_group.id,
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        logger.info("Superuser already assigned to system admins group")
        return

    association = UserGroupModel(user_id=superuser.id, group_id=admins_group.id)
    session.add(association)
    await session.flush()
    logger.info("Assigned superuser to system admins group")
