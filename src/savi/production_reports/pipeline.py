from datetime import datetime
from typing import Annotated

from src.core.bronze import write_to_bronze
from src.core.config import settings
from src.core.logger import logger
from src.savi.production_reports.extract_data import ProductionReportExtractor
from src.savi.production_reports.parser_data import ProductionReportParser
from src.savi.production_reports.schema import ProductionReportRow
from src.savi.production_reports.validate import validate_rows


class ProductionReportPipeline:
    def __init__(
        self,
        month_competency: Annotated[str, "Mês de competência, no formato MM/AAAA."],
    ):
        self.month_competency = month_competency
        self.bronze_path = settings.bronze_dir / "production_reports"

    def get_data(self) -> str:
        """
        Executa a pesquisa do relatório de produção e obtém o conteúdo do mesmo.

        Returns:
            str: Conteúdo do relatório de produção em HTML.
        """
        with ProductionReportExtractor() as obj:
            html_data = obj.fetch(
                month_competency=self.month_competency,
            )
            return html_data

    def process_data(self, html_data: str) -> list[ProductionReportRow]:
        """
        Processa os dados extraídos do relatório de produção. Valida os dados e
        retorna uma lista de linhas válidas.

        Args:
            html_data (str): Conteúdo do relatório de produção em HTML.

        Returns:
            list[ProductionReportRow]: Dados validados.
        """
        parsed_rows = ProductionReportParser(html_data).parse()
        valid_rows = validate_rows(parsed_rows)
        logger.info("Produções processadas: {} linhas válidas", len(valid_rows))
        return valid_rows

    def write_bronze_data(self, valid_rows: list[ProductionReportRow]) -> None:
        """
        Grava os dados de uma tabela Bronze. Faz upsert: uma linha cuja
        chave (competência + senha de autorização + guia) já existe é
        atualizada por completo, já que produção médica reflete o estado
        mais recente conhecido, não o histórico de mudanças.

        Args:
            valid_rows (list[ProductionReportRow]): Dados validados.
        """
        partition_value = datetime.strptime(self.month_competency, "%m/%Y").strftime(
            "%Y%m"
        )
        merge_predicate = (
            "target.dt_period = source.dt_period AND "
            "target.cd_auth_password = source.cd_auth_password AND "
            "target.nr_guide = source.nr_guide"
        )
        logger.info("Gravando dados de produção no Bronze para {}", partition_value)
        write_to_bronze(
            valid_rows,
            self.bronze_path,
            partition_value,
            merge_predicate=merge_predicate,
            update_on_match=True,
        )

    def main(self) -> None:
        """
        Executa a pesquisa do relatório de produção e valida os dados extraídos.
        """
        html_data = self.get_data()
        valid_rows = self.process_data(html_data)
        self.write_bronze_data(valid_rows)
