from typing import Generator

from bs4 import BeautifulSoup, Tag

from src.core.logger import logger


class PendingReportParser:
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
            parts = [s.strip() for s in td.strings if s.strip()]
            if len(parts) >= 2:
                return parts[0], " ".join(parts[1:])
        except AttributeError:
            logger.warning(
                "Erro ao extrair código/nome da célula: {}", len(td.contents)
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
            return td.get_text(strip=True)
        except AttributeError:
            logger.warning("Erro ao extrair texto da célula: {}", len(td.contents))
            return ""

    def _extract_situation(self, td: Tag) -> str:
        """
        Extrai o status da situação da célula. Se não encontrar, retorna o texto
        da célula.

        Args:
            td (Tag): Tag da célula.

        Returns:
            str: Status da situação da célula.
        """
        try:
            input_tag = td.find("input", attrs={"type": "submit"})
            if input_tag:
                return (input_tag.get("value") or "").strip()

            span = td.find("span", class_="label-senhapendente")
            if span:
                return span.get_text(strip=True)
        except AttributeError:
            logger.warning("Erro ao extrair situação da célula: {}", len(td.contents))
        return td.get_text(" ", strip=True)

    def _extract_observation(self, td: Tag) -> str | None:
        """
        Extrai a observação da célula. Se não encontrar, retorna None

        Args:
            td (Tag): Tag da célula.

        Returns:
            str: Observação da célula.
        """
        try:
            span = td.find("span", class_="tooltip-right")
            if span:
                return " ".join(span.get_text(" ", strip=True).split())
            return None
        except AttributeError:
            logger.warning("Erro ao extrair observação da célula: {}", len(td.contents))
            return None

    def _extract_password(self, td: Tag) -> str:
        """
        Extrai a senha da célula. Se não encontrar, retorna o texto da célula.

        Args:
            td (Tag): Tag da célula.

        Returns:
            str: Senha da célula.
        """
        try:
            full = td.get_text(" ", strip=True)
            tooltip = td.find("span", class_="tooltip-left")
            if tooltip:
                tip_text = tooltip.get_text(" ", strip=True)
                return full.replace(tip_text, "", 1).strip()
            return full
        except AttributeError:
            logger.warning("Erro ao extrair senha da célula: {}", len(td.contents))
            return ""

    def _parse_data_row(self, cells: list[Tag]) -> dict[str, str | None]:
        """
        Parseia uma linha de dados e retorna um dicionário com os dados.

        Args:
            cells (list[Tag]): Lista de células da linha.

        Returns:
            dict[str, str | None]: Dicionário com os dados da linha.
        """
        cd_patient, nm_patient = self._split_code_name(cells[1])
        cd_doctor, nm_doctor = self._split_code_name(cells[2])
        cd_procedure, nm_procedure = self._split_code_name(cells[3])

        return {
            "cd_auth_password": self._extract_password(cells[7]),
            "cd_patient": cd_patient,
            "nm_patient": nm_patient,
            "cd_doctor": cd_doctor,
            "nm_doctor": nm_doctor,
            "cd_procedure": cd_procedure,
            "nm_procedure": nm_procedure,
            "dt_authorization": self._text(cells[0]),
            "qt_authorized": self._text(cells[4]),
            "qt_pending": self._text(cells[5]),
            "tp_situation": self._extract_situation(cells[6]),
            "ds_observation": self._extract_observation(cells[6]),
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

        for tr in table.find_all("tr"):
            if tr.find("th"):
                continue

            cells = tr.find_all("td")
            if len(cells) != 8:
                logger.warning("Número de células não corresponde: {}", len(cells))
                continue

            yield self._parse_data_row(cells)

    def __iter__(self):
        return self.parse()
