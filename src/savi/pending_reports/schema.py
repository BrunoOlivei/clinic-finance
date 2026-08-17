from datetime import date, datetime

from pydantic import BaseModel, field_validator, model_validator


class PendingReportRow(BaseModel):
    cd_auth_password: str
    cd_patient: str
    nm_patient: str
    cd_doctor: str
    nm_doctor: str
    cd_procedure: str
    nm_procedure: str
    dt_authorization: date
    qt_authorized: int
    qt_pending: int
    tp_situation: str
    ds_observation: str | None

    @field_validator("dt_authorization", mode="before")
    @classmethod
    def _parse_br_date(cls, value: str) -> date:
        return datetime.strptime(value, "%d/%m/%Y").date()

    @field_validator("qt_authorized", "qt_pending", mode="before")
    @classmethod
    def _parse_quantity(cls, value: str) -> int:
        return int(value.replace(".", ""))

    @model_validator(mode="before")
    @classmethod
    def _split_doctor_code(cls, data: dict[str, str]) -> dict[str, str]:
        raw = data["cd_doctor"]
        code, separator, _ = raw.partition(" CRM")
        if not separator:
            raise ValueError(
                f"Formato de cd_doctor inesperado, CRM não encontrado: {raw!r}"
            )
        data["cd_doctor"] = code
        return data
