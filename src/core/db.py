from sqlalchemy import create_engine

from src.core.config import Environment, settings

engine = create_engine(
    settings.sqlalchemy_dsn,
    pool_pre_ping=True,
    echo=settings.environment == Environment.DEV,
)
