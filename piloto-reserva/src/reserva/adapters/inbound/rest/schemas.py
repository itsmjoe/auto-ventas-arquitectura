"""DTOs del adaptador REST de Reserva."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from reserva.domain.reserva import Reserva


class CrearReservaRequest(BaseModel):
    cotizacion_id: str = Field(..., min_length=1)
    cliente_id: str = Field(..., min_length=1)


class ReservaResponse(BaseModel):
    id: str
    cotizacion_id: str
    vehiculo_id: str
    cliente_id: str
    estado: str
    creada_en: datetime

    @classmethod
    def desde_dominio(cls, r: Reserva) -> ReservaResponse:
        return cls(
            id=r.id,
            cotizacion_id=r.cotizacion_id,
            vehiculo_id=r.vehiculo_id,
            cliente_id=r.cliente_id,
            estado=r.estado.value,
            creada_en=r.creada_en,
        )
