"""Entidad Reserva."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EstadoReserva(StrEnum):
    CONFIRMADA = "CONFIRMADA"
    RECHAZADA = "RECHAZADA"


@dataclass(frozen=True)
class Reserva:
    id: str
    cotizacion_id: str
    vehiculo_id: str
    cliente_id: str
    estado: EstadoReserva
    creada_en: datetime
