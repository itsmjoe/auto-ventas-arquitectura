"""Puertos del servicio de Reserva.

`CotizacionInfo` es el modelo que Reserva entiende de una cotización. El adaptador que
implementa `CotizacionPort` traduce la respuesta del servicio de Cotización a este
modelo (Anti-Corruption Layer): Reserva no depende del esquema interno del otro servicio.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from reserva.domain.reserva import Reserva


@dataclass(frozen=True)
class CotizacionInfo:
    id: str
    vehiculo_id: str
    total: Decimal
    disponible: bool
    expira_en: datetime


class CotizacionPort(Protocol):
    """Acceso a la cotización (otro microservicio)."""

    def obtener(self, cotizacion_id: str) -> CotizacionInfo | None:
        ...


class ReservaRepositoryPort(Protocol):
    def guardar(self, reserva: Reserva) -> None:
        ...

    def obtener(self, reserva_id: str) -> Reserva | None:
        ...
