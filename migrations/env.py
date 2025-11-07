import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# --- Пути ---
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

# --- Загрузка .env ---
load_dotenv(BASE_DIR / ".env")

# --- Импорт моделей ---
from models import Base  # src/models/__init__.py

# --- Конфигурация Alembic ---
config = context.config
fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL не найден в .env")

target_metadata = Base.metadata


def run_migrations_offline():
    """Offline mode (без реального подключения)."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Online mode (асинхронное подключение)."""
    connectable = create_async_engine(DATABASE_URL, echo=False)

    async with connectable.connect() as connection:

        def do_run_migrations(connection):
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run_migrations()