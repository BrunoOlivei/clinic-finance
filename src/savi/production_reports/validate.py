from typing import Iterable

from pydantic import ValidationError

from src.core.exceptions import ExtractionValidationError
from src.core.logger import logger
from src.savi.production_reports.schema import ProductionReportRow


def validate_rows(
    parsed_rows: Iterable[dict[str, str | None]],
) -> list[ProductionReportRow]:
    """
    Valida os dados extraídos do relatório de produção.

    Args:
        parsed_rows (Iterable[dict[str, str  |  None]]): Dados extraídos do
        relatório de produção.

    Raises:
        ExtractionValidationError: Se houver erros de validação.

    Returns:
        list[ProductionReportRow]: Dados validados.
    """
    valid_rows: list[ProductionReportRow] = []
    failures: list[tuple[dict, ValidationError]] = []

    for row in parsed_rows:
        try:
            valid_rows.append(ProductionReportRow.model_validate(row))
        except ValidationError as exc:
            failures.append((row, exc))

    if failures:
        for row, exc in failures:
            logger.bind(
                nr_guide=row.get("nr_guide"),
                errors=exc.errors(),
            ).error(
                "Linha de produção inválida",
            )
        raise ExtractionValidationError(
            f"{len(failures)} linha(s) de produção falharam na validação do contrato."
        )

    return valid_rows
