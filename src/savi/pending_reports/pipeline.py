from typing import Annotated

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

    def print_data(self, valid_rows):
        for row in valid_rows:
            print(row)

    def main(self) -> None:
        """
        Executa a pesquisa do relatório de pendências e valida os dados extraídos.
        """
        html_data = self.get_data()
        valid_rows = self.process_data(html_data)
        self.print_data(valid_rows)
