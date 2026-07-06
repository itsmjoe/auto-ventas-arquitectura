"""Adaptador outbound: cliente HTTP del microservicio de Cotización.

Aquí es donde un hexágono (Reserva) habla con otro (Cotización) por la red. Traduce la
respuesta del servicio de Cotización al modelo `CotizacionInfo` que Reserva entiende (ACL).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import httpx

from reserva.application.ports import CotizacionInfo


class CotizacionHttpClient:
    def __init__(
        self, base_url: str, timeout: float = 2.0, cliente: httpx.Client | None = None
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._cliente = cliente or httpx.Client(timeout=timeout)

    def obtener(self, cotizacion_id: str) -> CotizacionInfo | None:
        respuesta = self._cliente.get(f"{self._base_url}/cotizaciones/{cotizacion_id}")
        if respuesta.status_code == httpx.codes.NOT_FOUND:
            return None
        respuesta.raise_for_status()
        return self._a_dominio(respuesta.json())

    @staticmethod
    def _a_dominio(datos: dict) -> CotizacionInfo:
        return CotizacionInfo(
            id=datos["id"],
            vehiculo_id=datos["vehiculo_id"],
            total=Decimal(str(datos["total"])),
            disponible=bool(datos["disponible"]),
            expira_en=datetime.fromisoformat(datos["expira_en"]),
        )
