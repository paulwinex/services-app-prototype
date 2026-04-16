from logging.config import fileConfig
import dotenv

dotenv.load_dotenv()

from sqlalchemy import create_engine, pool

from alembic import context

alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

from app.shared.base_model import BaseDBModel
from app.modules.users.models import UserModel
from app.modules.groups.models import GroupModel
from app.modules.permissions.models import PermissionModel
from app.core.settings import get_settings

settings = get_settings()

target_metadata = BaseDBModel.metadata


def get_database_url():
    return settings.DB.dsn.replace("postgresql+asyncpg://", "postgresql://")


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
