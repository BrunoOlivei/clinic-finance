from datetime import datetime

from sqlalchemy import (Column, Date, DateTime, MetaData, String, Table, func,
                        select)
from sqlalchemy.dialects.postgresql import insert

from src.core.db import engine

metadata = MetaData()

extraction_checkpoints = Table(
    "extraction_checkpoints",
    metadata,
    Column("pipeline", String, primary_key=True),
    Column("month_competency", Date, primary_key=True),
    Column("extracted_at", DateTime, nullable=False),
)


def _ensure_schema() -> None:
    metadata.create_all(engine, checkfirst=True)


def record_checkpoint(pipeline: str, month_competency: str) -> None:
    _ensure_schema()
    competency_date = datetime.strptime(month_competency, "%m/%Y").date().replace(day=1)

    stmt = insert(extraction_checkpoints).values(
        pipeline=pipeline,
        month_competency=competency_date,
        extracted_at=datetime.now(),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["pipeline", "month_competency"],
        set_={"extracted_at": stmt.excluded.extracted_at},
    )

    with engine.begin() as conn:
        conn.execute(stmt)


def get_last_checkpoint(pipeline: str) -> str | None:
    _ensure_schema()
    stmt = select(func.max(extraction_checkpoints.c.month_competency)).where(
        extraction_checkpoints.c.pipeline == pipeline
    )

    with engine.connect() as conn:
        result = conn.execute(stmt).scalar()

    return result.strftime("%m/%Y") if result else None
