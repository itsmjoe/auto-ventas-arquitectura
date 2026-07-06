"""Puertos (interfaces) de la arquitectura hexagonal.

El dominio y los casos de uso dependen de estas abstracciones, nunca de
implementaciones concretas (ERP, banco, aseguradora, base de datos).
"""
from __future__ import annotations

from typing import Protocol

from cotizacion.domain.cotizacion import Cotizacion, Oferta
from cotizacion.domain.vehiculo import Vehiculo


class CatalogoPort(Protocol):
    """Origen de datos del vehículo (ERP / réplica de solo lectura)."""

    def obtener(self, vehiculo_id: str) -> Vehiculo | None:
        ...


class FinanciamientoPort(Protocol):
    """Cotización de préstamos con un banco socio."""

    async def cotizar(self, vehiculo: Vehiculo, cliente_id: str) -> list[Oferta]:
        ...


class SeguroPort(Protocol):
    """Cotización de seguros con una aseguradora socia."""

    async def cotizar(self, vehiculo: Vehiculo, cliente_id: str) -> list[Oferta]:
        ...


class CotizacionRepositoryPort(Protocol):
    """Persistencia de cotizaciones."""

    def guardar(self, cotizacion: Cotizacion, clave_idempotencia: str | None = None) -> None:
        ...

    def obtener(self, cotizacion_id: str) -> Cotizacion | None:
        ...

    def buscar_por_idempotencia(self, clave: str) -> Cotizacion | None:
        ...
