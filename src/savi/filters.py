from playwright.sync_api import Page

from src.core.config import settings
from src.savi.session import log_step


def select_month_competency(page: Page, month_competency: str) -> None:
    """
    Seleciona o mês de competência que se deseja extrair do relatório de produção.
    O mês deve ser passado no formato "MM/YYYY".

    Args:
        month_competency (str): Mês de competência, no formato "MM/YYYY".
    """
    with log_step(f"selecionar o mês de competência: {month_competency}"):
        page.select_option(settings.sel_mes, month_competency)


def fill_date_range(page: Page, start_day: str | None, end_day: str | None) -> None:
    """
    Preenche o forumulário de relatório de produção com dias que se deseja filtrar a
    competência.
    Os dias devem ser passados sempre no formato "DD"
    Eles só podem ser usados se uma competência for selecionada.

    Args:
        start_day (str | None): Dia de início do intervalo de datas, no formato "DD".
        end_day (str | None): Dia de fim do intervalo de datas, no formato "DD".
    """
    with log_step(f"preencher o intervalo de datas: {start_day} a {end_day}"):
        if start_day is not None:
            page.fill(settings.sel_dia_de, start_day)
        if end_day is not None:
            page.fill(settings.sel_dia_ate, end_day)
