from datetime import date, datetime

from pydantic import BaseModel, field_validator, model_validator


class ProductionReportRow(BaseModel):
    tp_service: str | None
    nm_branch: str | None
    dt_execution: date
    cd_patient: str
    nm_patient: str
    cd_doctor: str
    sg_doctor_state: str
    nm_doctor: str
    cd_procedure: str
    nm_procedure: str
    is_urgent: bool
    qt_authorized: int
    qt_executed: int
    dt_authorization: date
    nr_guide: str
    cd_auth_password: str

    @field_validator("nm_branch")
    @classmethod
    def _parse_branch(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.rsplit(" ", 1)[0]

    @field_validator("dt_execution", "dt_authorization", mode="before")
    @classmethod
    def _parse_br_date(cls, value: str) -> date:
        return datetime.strptime(value, "%d/%m/%Y").date()

    @model_validator(mode="before")
    @classmethod
    def _split_doctor_code(cls, data: dict[str, str]) -> dict[str, str]:
        raw = data["cd_doctor"]
        code, separator, state = raw.partition(" CRM ")
        if not separator:
            raise ValueError(
                f"Formato de cd_doctor inesperado, CRM não encontrado: {raw!r}"
            )
        data["cd_doctor"] = code
        data["sg_doctor_state"] = state
        return data

    @field_validator("is_urgent", mode="before")
    @classmethod
    def _parse_urgency(cls, value: str) -> bool:
        return value == "S"

    @field_validator("qt_authorized", "qt_executed", mode="before")
    @classmethod
    def _parse_quantity(cls, value: str) -> int:
        return int(value.replace(".", ""))
