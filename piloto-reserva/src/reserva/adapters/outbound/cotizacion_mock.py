"""Adaptador outbound: cotizaciones simuladas en memoria (mismo puerto que el HTTP)."""
from __future__ import annotations

from reserva.application.ports import CotizacionInfo


class CotizacionMock:
    def __init__(self, cotizaciones: dict[str, CotizacionInfo] | None = None) -> None:
        self._cotizaciones = cotizaciones or {}

    def obtener(self, cotizacion_id: str) -> CotizacionInfo | None:
        return self._cotizaciones.get(cotizacion_id)
