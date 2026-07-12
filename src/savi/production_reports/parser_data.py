from typing import Iterator

from bs4 import BeautifulSoup, Tag

from src.core.logger import logger


class ProductionReportParser:
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, "html.parser")

    def _split_code_name(self, td: Tag) -> tuple[str, str]:
        """
        Extrai o código e o nome de uma célula que contém um par de dados.

        Args:
            td (Tag): Tag da célula que contém o código e o nome.

        Returns:
            tuple[str, str]: Código e nome do par de dados.
        """
        try:
            b_content = td.find("b")
            if b_content:
                code = b_content.get_text(strip=True)
                name = td.get_text(" ", strip=True).replace(code, "", 1).strip()
                return code, name
            return "", td.get_text(" ", strip=True)
        except AttributeError:
            logger.warning(
                "Erro ao extrair código/nome da célula {}:", len(td.contents)
            )
            return "", td.get_text(" ", strip=True)

    def _text(self, td: Tag) -> str:
        """
        Extrai o texto de uma célula.

        Args:
            td (Tag): Tag da célula.

        Returns:
            str: Texto da célula.
        """
        try:
            return td.get_text(" ", strip=True)
        except AttributeError:
            logger.warning("Erro ao extrair texto da célula: {}", len(td.contents))
            return ""

    def _extract_table_header(self, th: Tag) -> str:
        """
        Extrai o cabeçalho de uma célula da tabela.

        Args:
            th (Tag): Tag da célula.

        Returns:
            str: Cabeçalho da célula.
        """
        try:
            header = th.get_text(strip=True).split(":", 1)[-1].strip()
        except AttributeError:
            logger.warning("Erro ao extrair cabeçalho da célula {}", th)
            return th.get_text(strip=True)
        else:
            logger.info(f"Cabeçalho da célula {th}: {header}")
            return header

    def _parse_data_row(
        self, cells: list[Tag], service: str | None, branch: str | None
    ) -> dict[str, str]:
        """
        Extrai os dados de uma linha da tabela.

        Args:
            cells (list): Lista de células da linha.
            service (str | None): Código do serviço, se houver.
            branch (str | None): Código do ramo, se houver.

        Returns:
            dict[str, str]: Dicionário com os dados da linha.
        """
        user_code, user_name = self._split_code_name(cells[1])
        doctor_code, doctor_name = self._split_code_name(cells[2])
        procedure_code, procedure_name = self._split_code_name(cells[3])

        return {
            "service": service,
            "branch": branch,
            "data_execution": self._text(cells[0]),
            "user_code": user_code,
            "user_name": user_name,
            "doctor_code": doctor_code,
            "doctor_name": doctor_name,
            "procedure_code": procedure_code,
            "procedure_name": procedure_name,
            "urgency": self._text(cells[4]),
            "qty_authorized": self._text(cells[5]),
            "qty_performed": self._text(cells[6]),
            "date_authorization": self._text(cells[7]),
            "number_guide": self._text(cells[8]),
            "password": self._text(cells[9]),
        }

    def parse(self) -> Iterator[dict[str, str]]:
        """
        Parseia a tabela de dados e retorna um dicionário com os dados.

        Yields:
            Iterator[dict[str, str]]: Dicionário com os dados da tabela.
        """
        table = self.soup.find("table")
        if table is None:
            return

        service = None
        branch = None
        for tr in table.find_all("tr"):
            header_1 = tr.find("th", class_="cabecalho1")
            if header_1:
                service = self._extract_table_header(header_1)
                branch = None
                continue

            header_2 = tr.find("th", class_="cabecalho2")
            if header_2:
                branch = self._extract_table_header(header_2)
                continue

            if tr.find("th"):
                logger.warning("Encontrado cabeçalho: {}", len(tr.find("th")))
                continue

            cells = tr.find_all("td")
            if len(cells) != 10:
                logger.warning("Número de células não corresponde: {}", len(cells))
                continue

            yield self._parse_data_row(cells, service, branch)

    def __iter__(self):
        return self.parse()
