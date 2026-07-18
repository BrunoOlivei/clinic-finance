from json import JSONDecodeError
from typing import Any

import requests

from src.communicare.attendance_status import AttendanceStatus
from src.communicare.schedule_status import ScheduleStatus
from src.core.config import settings
from src.core.logger import logger


class AdministrativeReport:
    def __init__(
        self,
        start_date: str,
        end_date: str,
        attendance_status: AttendanceStatus | None = None,
        schedule_status: ScheduleStatus | None = None,
    ) -> None:
        self.clinic = "1274,0"
        self.professional = "262586,0"
        self.start_date = start_date
        self.end_date = end_date
        self.attendance_status = attendance_status
        self.schedule_status = schedule_status

    def _post_and_parse(
        self,
        url: str,
        payload: dict[str, Any],
        context: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """
        Executa um POST e devolve o corpo já decodificado como JSON,
        logando e propagando qualquer erro de HTTP ou de decodificação.

        Args:
            url (str): URL de destino da requisição.
            payload (dict[str, Any]): Corpo da requisição.
            context (str): Descrição da operação, usada nas mensagens de log
                (ex.: "fazer login", "executar o relatório").
            headers (dict[str, str] | None): Cabeçalhos da requisição.

        Returns:
            Any: Corpo da resposta decodificado como JSON.
        """
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                message=f"Erro ao {context}: {e.response.status_code} {e.response.reason}",
                exc_info=e,
            )
            raise
        except Exception as e:
            logger.error(
                message=f"Erro inesperado ao {context}: {e}",
                exc_info=e,
            )
            raise
        try:
            return response.json()
        except JSONDecodeError as e:
            logger.error(
                message=f"Erro ao decodificar resposta ao {context}: {e}",
                exc_info=e,
            )
            raise
        except Exception as e:
            logger.error(
                message=f"Erro inesperado ao decodificar resposta ao {context}: {e}",
                exc_info=e,
            )
            raise

    def login(self) -> str:
        """
        Login no sistema de gerenciamento de pacientes.

        Returns:
            str: Token de acesso.
        """
        payload = {
            "username": settings.communicare_username.get_secret_value(),
            "password": settings.communicare_password.get_secret_value(),
        }
        data = self._post_and_parse(
            settings.communicare_url_login, payload, context="fazer login"
        )
        try:
            token = data["accessToken"]
        except KeyError as e:
            logger.error(
                message=f"Erro ao obter token: {e.args[0]}",
                exc_info=e,
            )
            raise
        logger.info("Login bem-sucedido.")
        return token

    def set_attendance_status(self) -> str:
        """
        Define o status de atendimento do paciente.

        Returns:
            str: Status de atendimento do paciente.
        """
        if self.attendance_status is None:
            return "'Atendimento não iniciado', 'Atendimento não finalizado', 'Faltou', 'Finalizado conclusivo', 'Finalizado inconclusivo', 'Finalizado automaticamente', ''"
        else:
            return f"'{self.attendance_status.value}', ''"

    def set_schedule_status(self) -> str:
        """
        Define o status de agendamento do paciente.

        Returns:
            str: Status de agendamento do paciente.
        """
        if self.schedule_status is None:
            return "'Agendado', 'Reagendado', 'Reagendamento', 'Fila', 'Encaixe', 'Cancelado', ''"
        else:
            return f"'{self.schedule_status.value}', ''"

    def administrative_report(self, token: str) -> list[dict[str, Any]]:
        """
        Executa o relatório administrativo de atendimento.

        Args:
            token (str): Token de acesso.

        Returns:
            list[dict[str, Any]]: Dados do relatório administrativo de atendimento.
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "new-auth": f"Bearer {token}",
            "Origin": "https://app.communicare.com.br",
        }
        payload = {
            "clinic": self.clinic,
            "professional": self.professional,
            "procedure": "5230,5227,5228",
            "initialDate": self.start_date,
            "finalDate": self.end_date,
            "patient": "%%",
            "scheduleStatus": self.set_schedule_status(),
            "attendanceStatus": self.set_attendance_status(),
            "fit": [True, False],
            "teleconsulta": [True, False],
            "activePatients": "Todos",
            "paymentType": ["Convênio"],
            "healthPlan": [{"id": 429, "name": "HAPVIDA ASSISTÊNCIA MÉDICA S.A. "}],
            "team": [],
        }
        data = self._post_and_parse(
            settings.communicare_url_attendance,
            payload,
            context="executar o relatório",
            headers=headers,
        )
        logger.info("Relatório executado com sucesso.")
        return data

    def main(self) -> list[dict[str, Any]]:
        """
        Executa o relatório administrativo de atendimento.

        Returns:
            list[dict[str, Any]]: Dados do relatório administrativo de atendimento.
        """
        token = self.login()
        data = self.administrative_report(token)
        return data
