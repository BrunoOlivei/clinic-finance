from pathlib import Path

import pyarrow as pa
from deltalake import write_deltalake
from deltalake.exceptions import SchemaMismatchError
from pydantic import BaseModel

from src.core.logger import logger


def write_to_bronze(
    rows: list[BaseModel],
    table_path: Path,
    month_competency: str,
) -> None:
    """
    Grava os dados de uma tabela Bronze.

    Args:
        rows (list[BaseModel]): Dados a gravar na tabela Bronze.
        table_path (Path): Caminho para a tabela Bronze.
        month_competency (str): Mês de competência, no formato "YYYYMM".
    """
    if not rows:
        logger.info("Nenhuma linha para gravar no Bronze — nada a fazer.")
        return
    try:
        records = [row.model_dump() for row in rows]
        for record in records:
            record["mes_competencia"] = month_competency
        table = pa.Table.from_pylist(records)
        write_deltalake(
            table_path,
            table,
            partition_by=["mes_competencia"],
            mode="append",  # provisório — idempotência é o CLIN-0025
        )
    except SchemaMismatchError:
        logger.exception(
            "Schema dos dados não bate com o schema já gravado na tabela Bronze — "
            "provável mudança no contrato Pydantic"
        )
        raise
    except Exception:
        logger.exception("Erro ao gravar dados no Bronze")
        raise
