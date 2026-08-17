from typing import Iterable

from pydantic import ValidationError

from src.core.exceptions import ExtractionValidationError
from src.core.logger import logger
from src.savi.pending_reports.schema import PendingReportRow


def validate_rows(
    parsed_rows: Iterable[dict[str, str | None]],
) -> list[PendingReportRow]:
    """
    Valida os dados extraídos do relatório de pendências.

    Args:
        parsed_rows (Iterable[dict[str, str  |  None]]): Dados extraídos do
        relatório de pendências.

    Raises:
        ExtractionValidationError: Se houver erros de validação.

    Returns:
        list[PendingReportRow]: Dados validados.
    """
    valid_rows: list[PendingReportRow] = []
    failures: list[tuple[dict, ValidationError]] = []

    for row in parsed_rows:
        try:
            valid_rows.append(PendingReportRow.model_validate(row))
        except ValidationError as exc:
            failures.append((row, exc))

    if failures:
        for row, exc in failures:
            logger.bind(
                cd_patient=row.get("cd_patient"),
                cd_procedure=row.get("cd_procedure"),
                dt_authorization=row.get("dt_authorization"),
                errors=exc.errors(),
            ).error(
                "Linha de pendências inválida",
            )
        raise ExtractionValidationError(
            f"{len(failures)} linha(s) de pendências falharam na validação do contrato."
        )

    return valid_rows
