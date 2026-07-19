from typing import Generator

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
    ) -> dict[str, str | None]:
        """
        Extrai os dados de uma linha da tabela.

        Args:
            cells (list): Lista de células da linha.
            service (str | None): Código do serviço, se houver.
            branch (str | None): Código do ramo, se houver.

        Returns:
            dict[str, str]: Dicionário com os dados da linha.
        """
        cd_patient, nm_patient = self._split_code_name(cells[1])
        cd_doctor, nm_doctor = self._split_code_name(cells[2])
        cd_procedure, nm_procedure = self._split_code_name(cells[3])

        return {
            "tp_service": service,
            "nm_branch": branch,
            "dt_execution": self._text(cells[0]),
            "cd_patient": cd_patient,
            "nm_patient": nm_patient,
            "cd_doctor": cd_doctor,
            "nm_doctor": nm_doctor,
            "cd_procedure": cd_procedure,
            "nm_procedure": nm_procedure,
            "is_urgent": self._text(cells[4]),
            "qt_authorized": self._text(cells[5]),
            "qt_executed": self._text(cells[6]),
            "dt_authorization": self._text(cells[7]),
            "nr_guide": self._text(cells[8]),
            "cd_auth_password": self._text(cells[9]),
        }

    def parse(self) -> Generator[dict[str, str | None]]:
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
