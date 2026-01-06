from logging.config import fileConfig
import os

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool



load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base + import all models via app.models registry
from app.db import Base  # noqa: E402
import app.models  # noqa: F401, E402


target_metadata = Base.metadata

VERSION_TABLE_SCHEMA = "SWORD"


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set in .env")
    return url


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema=VERSION_TABLE_SCHEMA,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_database_url()
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=VERSION_TABLE_SCHEMA,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
