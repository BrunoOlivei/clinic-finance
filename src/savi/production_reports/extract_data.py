from src.core.config import settings
from src.savi.filters import fill_date_range, select_month_competency
from src.savi.session import SaviSession, log_step, reauth_on_expired


class ProductionReportExtractor(SaviSession):
    def _select_patient(self, patient_code: str) -> None:
        """
        Seleciona o código do paciente que se deseja filtrar o relatório de produção.

        Args:
            patient_code (str): Código do paciente que se deseja filtrar o relatório
            de produção.
        """
        with log_step(f"selecionar o código do paciente: {patient_code}"):
            self.page.fill(settings.sel_user_code, patient_code)
            self.page.click(settings.sel_search_user)

    def _search(self) -> None:
        """
        Executa a pesquisa do relatório de produção.
        """
        with log_step("pesquisar o relatório de produção"):
            with self.page.expect_response(
                lambda response: (
                    "relatorio_producao.faces" in response.url
                    and response.request.method == "POST"
                )
            ):
                self.page.click(settings.sel_pesquisar)

    @reauth_on_expired
    def fetch(
        self,
        month_competency: str,
        start_day: str | None = None,
        end_day: str | None = None,
        patient_code: str | None = None,
    ) -> str:
        """
        Executa a pesquisa do relatório de produção e obtém o conteúdo do mesmo.

        Args:
            month_competency (str): Mês de competência, no formato "MM/YYYY".
            start_day (str | None): Dia de início do intervalo de datas, no
            formato "DD".
            end_day (str | None): Dia de fim do intervalo de datas, no formato "DD".
            patient_code (str | None): Código do paciente que se deseja filtrar o
            relatório de produção.

        Returns:
            str: Conteúdo do relatório de produção em HTML.
        """
        with log_step("acessar a página de relatório de produção"):
            self.page.goto(settings.url_producao)
            self.page.wait_for_load_state("networkidle")
            self._assert_logged_in()

        select_month_competency(self.page, month_competency)
        fill_date_range(self.page, start_day, end_day)
        if patient_code is not None:
            self._select_patient(patient_code)

        self._search()
        self.page.wait_for_load_state("networkidle")

        with log_step("obter o conteúdo do relatório de produção"):
            html = self.page.content()

        return html
