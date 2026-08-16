from sqlalchemy import create_engine, text

from src.core.config import Environment, settings

engine = create_engine(
    settings.sqlalchemy_dsn,
    pool_pre_ping=True,
    echo=settings.environment == Environment.DEV,
    connect_args={"options": "-c search_path=gold,public"},
)


def run_query(sql: str) -> list[dict]:
    with engine.connect() as conn:
        return [dict(row) for row in conn.execute(text(sql)).mappings()]