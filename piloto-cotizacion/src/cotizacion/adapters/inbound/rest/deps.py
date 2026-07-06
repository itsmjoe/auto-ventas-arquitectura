"""Composición/inyección de dependencias del adaptador REST (wiring hexagonal).

Aquí se ensamblan los adaptadores concretos con el caso de uso. Es el único lugar
que conoce implementaciones concretas.
"""
from __future__ import annotations

from functools import lru_cache

from cotizacion.adapters.outbound.aseguradora_mock import AseguradoraMock
from cotizacion.adapters.outbound.banco_mock import BancoMock
from cotizacion.adapters.outbound.erp_catalogo_mock import ERPCatalogoMock
from cotizacion.adapters.outbound.repo_memoria import RepositorioMemoria
from cotizacion.application.crear_cotizacion import CrearCotizacion
from cotizacion.config import get_settings


@lru_cache
def get_repositorio() -> RepositorioMemoria:
    return RepositorioMemoria()


@lru_cache
def get_crear_cotizacion() -> CrearCotizacion:
    s = get_settings()
    return CrearCotizacion(
        catalogo=ERPCatalogoMock(),
        financiamiento=BancoMock(modo=s.modo_banco),
        seguro=AseguradoraMock(modo=s.modo_aseguradora),
        repositorio=get_repositorio(),
        tasa_impuesto=s.tasa_impuesto,
        vigencia_minutos=s.vigencia_minutos,
        timeout_socios=s.timeout_socios,
    )
