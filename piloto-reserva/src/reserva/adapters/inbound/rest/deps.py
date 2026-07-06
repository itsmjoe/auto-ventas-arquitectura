"""Wiring del servicio de Reserva: enchufa mock o cliente HTTP según configuración."""
from __future__ import annotations

from functools import lru_cache

from reserva.adapters.outbound.cotizacion_http import CotizacionHttpClient
from reserva.adapters.outbound.cotizacion_mock import CotizacionMock
from reserva.adapters.outbound.repo_memoria import RepositorioMemoria
from reserva.application.crear_reserva import CrearReserva
from reserva.application.ports import CotizacionPort
from reserva.config import get_settings


@lru_cache
def get_repositorio() -> RepositorioMemoria:
    return RepositorioMemoria()


def _construir_cotizaciones() -> CotizacionPort:
    s = get_settings()
    if s.cotizacion_url:
        return CotizacionHttpClient(s.cotizacion_url, timeout=s.timeout)
    return CotizacionMock()


@lru_cache
def get_crear_reserva() -> CrearReserva:
    return CrearReserva(
        cotizaciones=_construir_cotizaciones(),
        repositorio=get_repositorio(),
    )
