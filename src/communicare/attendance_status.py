from enum import StrEnum


class AttendanceStatus(StrEnum):
    ATENDIMENTO_NAO_INICIADO = "Atendimento não iniciado"
    ATENDIMENTO_NAO_FINALIZADO = "Atendimento não finalizado"
    FALTOU = "Faltou"
    FINALIZADO_CONCLUSIVO = "Finalizado conclusivo"
    FINALIZADO_INCONCLUSIVO = "Finalizado inconclusivo"
    FINALIZADO_AUTOMATICAMENTE = "Finalizado automaticamente"
    EMPTY = ""
