from enum import StrEnum


class ScheduleStatus(StrEnum):
    AGENDADO = "Agendado"
    REAGENDADO = "Reagendado"
    REAGENDAMENTO = "Reagendamento"
    FILA = "Fila"
    ENCAIXE = "Encaixe"
    CANCELADO = "Cancelado"
    EMPTY = ""
