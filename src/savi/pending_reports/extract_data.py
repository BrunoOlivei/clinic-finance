from src.core.config import settings
from src.savi.filters import fill_date_range, select_month_competency
from src.savi.pending_reports.status import PendingStatus
from src.savi.session import SaviSession, log_step, reauth_on_expired


class PendingReportExtractor(SaviSession):
    def _select_status(self, status: PendingStatus) -> None:
        """
        Seleciona o status (situação) que se deseja filtrar o relatório de pendências,
        TODAS é o valor padrão.

        Args:
            status (PendingStatus): Status (situação) que se deseja filtrar o relatório
            de pendências.
        """
        with log_step(f"selecionar o status: {status}"):
            self.page.select_option(settings.pend_sel_situacao, status)

    def _select_patient(self, patient_code: str) -> None:
        """
        Seleciona o código do paciente que se deseja filtrar o relatório de pendências.

        Args:
            patient_code (str): Código do paciente que se deseja filtrar o relatório
            de pendências.
        """
        with log_step(f"selecionar o código do paciente: {patient_code}"):
            self.page.fill(settings.sel_user_code, patient_code)
            self.page.click(settings.pend_sel_search_user)

    def _search(self) -> None:
        """
        Executa a pesquisa do relatório de pendências.
        """
        with log_step("pesquisar o relatório de pendências"):
            with self.page.expect_response(
                lambda response: (
                    "relatorio_pendencia.faces" in response.url
                    and response.request.method == "POST"
                )
            ):
                self.page.click(settings.pend_sel_pesquisar)

    @reauth_on_expired
    def fetch(
        self,
        month_competency: str,
        start_day: str | None = None,
        end_day: str | None = None,
        patient_code: str | None = None,
        status: PendingStatus | None = None,
    ) -> str:
        """
        Executa a pesquisa do relatório de pendências e obtém o conteúdo do mesmo.

        Args:
            month_competency (str): Mês de competência, no formato "MM/YYYY".
            start_day (str | None): Dia de início do intervalo de datas, no
            formato "DD".
            end_day (str | None): Dia de fim do intervalo de datas, no formato "DD".
            patient_code (str | None): Código do paciente que se deseja filtrar o
            relatório de pendências.
            status (PendingStatus | None): Status (situação) que se deseja filtrar
            o relatório de pendências.

        Returns:
            str: Conteúdo do relatório de pendências em HTML.
        """
        with log_step("acessar a página de relatório de pendências"):
            self.page.goto(settings.url_pendencias)
            self.page.wait_for_timeout(1500)
            self._assert_logged_in()

        select_month_competency(self.page, month_competency)
        fill_date_range(self.page, start_day, end_day)

        if patient_code is not None:
            self._select_patient(patient_code)
        if status is not None:
            self._select_status(status)

        self._search()
        self.page.wait_for_timeout(1500)
        with log_step("definir o número de registros a serem exibidos"):
            self.page.select_option(settings.pend_sel_pagination, label="10000")
            self.page.wait_for_timeout(1500)

        with log_step("obter o conteúdo do relatório de pendências"):
            html = self.page.content()

        return html
