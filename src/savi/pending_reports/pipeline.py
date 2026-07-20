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
        Grava os dados de uma tabela Bronze. Não faz upsert: quando a
        combinação de campos já existe (nada mudou desde a última
        extração), a linha é ignorada; quando difere em qualquer campo
        (senha, situação, procedimento, etc.), insere uma linha nova, pra
        manter o histórico de como cada pendência evoluiu.

        Args:
            valid_rows (list[PendingReportRow]): Dados validados.
        """
        partition_value = datetime.strptime(self.month_competency, "%m/%Y").strftime(
            "%Y%m"
        )
        merge_predicate = (
            "target.mes_competencia = source.mes_competencia AND "
            "target.cd_patient = source.cd_patient AND "
            "target.nm_patient = source.nm_patient AND "
            "target.cd_doctor = source.cd_doctor AND "
            "target.nm_doctor = source.nm_doctor AND "
            "target.cd_procedure = source.cd_procedure AND "
            "target.cd_auth_password = source.cd_auth_password AND "
            "target.tp_situation = source.tp_situation AND "
            "target.qt_authorized = source.qt_authorized AND "
            "target.qt_pending = source.qt_pending AND "
            "target.dt_authorization = source.dt_authorization AND "
            "(target.ds_observation = source.ds_observation "
            "OR (target.ds_observation IS NULL AND source.ds_observation IS NULL))"
        )
        logger.info("Gravando dados de pendências no Bronze para {}", partition_value)
        write_to_bronze(
            valid_rows,
            self.bronze_path,
            partition_value,
            merge_predicate=merge_predicate,
            update_on_match=False,
        )

    def main(self) -> None:
        """
        Executa a pesquisa do relatório de pendências e valida os dados extraídos.
        """
        html_data = self.get_data()
        valid_rows = self.process_data(html_data)
        self.write_bronze_data(valid_rows)
