from datetime import datetime
from pathlib import Path

import pyarrow as pa
from deltalake import DeltaTable, write_deltalake
from deltalake.exceptions import SchemaMismatchError
from pydantic import BaseModel

from src.core.logger import logger


def write_to_bronze(
    rows: list[BaseModel],
    table_path: Path,
    month_competency: str,
    merge_predicate: str,
    update_on_match: bool,
) -> None:
    """
    Grava os dados de uma tabela Bronze, fazendo upsert idempotente via merge.

    Na primeira escrita (tabela ainda não existe), grava direto. Nas
    seguintes, faz merge contra a tabela existente: quando `update_on_match`
    é True, uma linha cuja chave já existe é atualizada (preservando o
    `created_at` original e atualizando `updated_at`); quando é False, uma
    linha cuja chave já existe é ignorada (usado pra manter histórico em
    vez de sobrescrever) e só ganha `created_at`, sem `updated_at`.

    Args:
        rows (list[BaseModel]): Dados a gravar na tabela Bronze.
        table_path (Path): Caminho para a tabela Bronze.
        month_competency (str): Mês de competência, no formato "YYYYMM".
        merge_predicate (str): Condição de match do merge (ex.:
            "target.nr_guide = source.nr_guide").
        update_on_match (bool): Se True, atualiza a linha quando a chave já
            existe (também recebe `updated_at`); se False, só insere quando
            não existe (não atualiza, não recebe `updated_at`).
    """
    if not rows:
        logger.info("Nenhuma linha para gravar no Bronze — nada a fazer.")
        return

    try:
        now = datetime.now()
        records = [row.model_dump() for row in rows]
        for record in records:
            record["mes_competencia"] = month_competency
            record["created_at"] = now
            if update_on_match:
                record["updated_at"] = now
        table = pa.Table.from_pylist(records)

        if not DeltaTable.is_deltatable(str(table_path)):
            write_deltalake(
                table_path,
                table,
                partition_by=["mes_competencia"],
                mode="append",
            )
            return

        dt = DeltaTable(table_path)
        merger = dt.merge(
            source=table,
            predicate=merge_predicate,
            source_alias="source",
            target_alias="target",
        ).when_not_matched_insert_all()

        if update_on_match:
            update_columns = {
                col: f"source.{col}"
                for col in table.column_names
                if col != "created_at"
            }
            merger = merger.when_matched_update(updates=update_columns)

        merger.execute()
    except SchemaMismatchError:
        logger.exception(
            "Schema dos dados não bate com o schema já gravado na tabela Bronze — "
            "provável mudança no contrato Pydantic"
        )
        raise
    except Exception:
        logger.exception("Erro ao gravar dados no Bronze")
        raise
