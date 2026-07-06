"""Composición/inyección de dependencias del adaptador REST (wiring hexagonal).

Aquí se ensamblan los adaptadores concretos con el caso de uso. Es el único lugar
que conoce implementaciones concretas.
"""
from __future__ import annotations

from functools import lru_cache

from cotizacion.adapters.outbound.aseguradora_http import AseguradoraHttpClient
from cotizacion.adapters.outbound.aseguradora_mock import AseguradoraMock
from cotizacion.adapters.outbound.banco_http import BancoHttpClient
from cotizacion.adapters.outbound.banco_mock import BancoMock
from cotizacion.adapters.outbound.catalogo_http import CatalogoHttpClient
from cotizacion.adapters.outbound.erp_catalogo_mock import ERPCatalogoMock
from cotizacion.adapters.outbound.repo_memoria import RepositorioMemoria
from cotizacion.application.crear_cotizacion import CrearCotizacion
from cotizacion.application.ports import CatalogoPort, FinanciamientoPort, SeguroPort
from cotizacion.config import get_settings


@lru_cache
def get_repositorio() -> RepositorioMemoria:
    return RepositorioMemoria()


def _construir_catalogo() -> CatalogoPort:
    """Aquí se decide qué mundo hay detrás del puerto: mock o microservicio HTTP."""
    s = get_settings()
    if s.catalogo_url:
        return CatalogoHttpClient(s.catalogo_url, timeout=s.timeout_socios)
    return ERPCatalogoMock()


def _construir_banco() -> FinanciamientoPort:
    s = get_settings()
    if s.banco_url:
        return BancoHttpClient(s.banco_url, timeout=s.timeout_socios)
    return BancoMock(modo=s.modo_banco)


def _construir_aseguradora() -> SeguroPort:
    s = get_settings()
    if s.aseguradora_url:
        return AseguradoraHttpClient(s.aseguradora_url, timeout=s.timeout_socios)
    return AseguradoraMock(modo=s.modo_aseguradora)


@lru_cache
def get_crear_cotizacion() -> CrearCotizacion:
    s = get_settings()
    return CrearCotizacion(
        catalogo=_construir_catalogo(),
        financiamiento=_construir_banco(),
        seguro=_construir_aseguradora(),
        repositorio=get_repositorio(),
        tasa_impuesto=s.tasa_impuesto,
        vigencia_minutos=s.vigencia_minutos,
        timeout_socios=s.timeout_socios,
    )
