from src.core.config import settings
from src.core.savi_session import SaviSession, log_step


class ProductionReportExtractor(SaviSession):
    def _select_month_competency(self, month_competency: str) -> None:
        """
        Seleciona o mês de competência que se deseja extrair do relatório de produção.
        O mês deve ser passado no formato "MM/YYYY".

        Args:
            month_competency (str): Mês de competência, no formato "MM/YYYY".
        """
        with log_step(f"selecionar a competência do mês: {month_competency}"):
            self.page.select_option(settings.sel_mes, month_competency)

    def _fill_date_range(self, start_day: str | None, end_day: str | None) -> None:
        """
        Preenche o forumulário de relatório de produção com dias que se deseja filtrar a competência.
        Os dias devem ser passados sempre no formato "DD"
        Eles só podem ser usados se uma competência for selecionada.

        Args:
            start_day (str | None): Dia de início do intervalo de datas, no formato "DD".
            end_day (str | None): Dia de fim do intervalo de datas, no formato "DD".
        """
        with log_step(f"preencher o intervalo de datas: {start_day} a {end_day}"):
            if start_day is not None:
                self.page.fill(settings.sel_dia_de, start_day)
            if end_day is not None:
                self.page.fill(settings.sel_dia_ate, end_day)

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

    def fetch(
        self,
        month_competency: str,
        start_day: str | None = None,
        end_day: str | None = None,
    ) -> str:
        """
        Executa a pesquisa do relatório de produção e obtém o conteúdo do mesmo.

        Args:
            month_competency (str): Mês de competência, no formato "MM/YYYY".
            start_day (str | None): Dia de início do intervalo de datas, no formato "DD".
            end_day (str | None): Dia de fim do intervalo de datas, no formato "DD".

        Returns:
            str: Conteúdo do relatório de produção em HTML.
        """
        with log_step("acessar a página de relatório de produção"):
            self.page.goto(settings.url_producao)
            self.page.wait_for_load_state("networkidle")
            self._assert_logged_in()

        self._select_month_competency(month_competency)
        self._fill_date_range(start_day, end_day)
        self._search()
        self.page.wait_for_load_state("networkidle")

        with log_step("obter o conteúdo do relatório de produção"):
            html = self.page.content()

        return html
