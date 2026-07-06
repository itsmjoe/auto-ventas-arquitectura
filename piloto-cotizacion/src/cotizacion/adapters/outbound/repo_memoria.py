"""Adaptador outbound: repositorio de cotizaciones en memoria.

Suficiente para el piloto; en producción se reemplaza por un adaptador
SQLAlchemy/RDS sin tocar dominio ni casos de uso.
"""
from __future__ import annotations

from cotizacion.domain.cotizacion import Cotizacion


class RepositorioMemoria:
    def __init__(self) -> None:
        self._por_id: dict[str, Cotizacion] = {}
        self._por_clave: dict[str, str] = {}

    def guardar(self, cotizacion: Cotizacion, clave_idempotencia: str | None = None) -> None:
        self._por_id[cotizacion.id] = cotizacion
        if clave_idempotencia:
            self._por_clave[clave_idempotencia] = cotizacion.id

    def obtener(self, cotizacion_id: str) -> Cotizacion | None:
        return self._por_id.get(cotizacion_id)

    def buscar_por_idempotencia(self, clave: str) -> Cotizacion | None:
        cotizacion_id = self._por_clave.get(clave)
        return self._por_id.get(cotizacion_id) if cotizacion_id else None
