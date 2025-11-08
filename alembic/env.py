import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# --- Make sure Alembic can import the app correctly ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app_path = os.path.join(project_root, "apps", "sales-agent-api")
sys.path.insert(0, app_path)

# --- Load .env ---
load_dotenv(os.path.join(project_root, ".env"))

# --- Import Base and models ---
from app.services.db import Base, import_all_models
import_all_models()  # ✅ ensures all models (including fulfillments) are loaded
from app.models import product, inventory, order, customer, loyalty  # 👈 include all models

# --- Alembic Config ---
config = context.config

# Override DB URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# --- Logging Config ---
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Target Metadata ---
target_metadata = Base.metadata


# --- Migration Functions ---
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# --- Run the right mode ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
