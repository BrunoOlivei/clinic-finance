from datetime import datetime
from typing import Annotated

from src.core.bronze import write_to_bronze
from src.core.config import settings
from src.core.logger import logger
from src.savi.pending_reports.extract_data import PendingReportExtractor
from src.savi.pending_reports.parser_data import PendingReportParser
from src.savi.pending_reports.schema import PendingReportRow
from src.savi.pending_reports.validate import validate_rows


class PendingReportPipeline:
    def __init__(
        self,
        month_competency: Annotated[str, "Mês de competência, no formato MM/AAAA."],
    ):
        self.month_competency = month_competency
        self.bronze_path = settings.bronze_dir / "pending_reports"

    def get_data(self) -> str:
        """
        Executa a pesquisa do relatório de pendências e obtém o conteúdo do mesmo.

        Returns:
            str: Conteúdo do relatório de pendências em HTML.
        """
        with PendingReportExtractor() as obj:
            html_data = obj.fetch(
                month_competency=self.month_competency,
            )
            return html_data

    def process_data(self, html_data: str) -> list[PendingReportRow]:
        """
        Processa os dados extraídos do relatório de pendências. Valida os dados
        e retorna uma lista de linhas válidas.

        Args:
            html_data (str): Conteúdo do relatório de pendências em HTML.

        Returns:
            list[PendingReportRow]: Dados validados.
        """
        parsed_rows = PendingReportParser(html_data).parse()
        valid_rows = validate_rows(parsed_rows)
        logger.info("Pendências processadas: {} linhas válidas", len(valid_rows))
        return valid_rows

    def write_bronze_data(self, valid_rows: list[PendingReportRow]) -> None:
        """
        Grava os dados de uma tabela Bronze.

        Args:
            valid_rows (list[PendingReportRow]): Dados validados.
        """
        partition_value = datetime.strptime(self.month_competency, "%m/%Y").strftime(
            "%Y%m"
        )
        logger.info("Gravando dados de pendências no Bronze para {}", partition_value)
        write_to_bronze(valid_rows, self.bronze_path, partition_value)

    def main(self) -> None:
        """
        Executa a pesquisa do relatório de pendências e valida os dados extraídos.
        """
        html_data = self.get_data()
        valid_rows = self.process_data(html_data)
        self.write_bronze_data(valid_rows)
