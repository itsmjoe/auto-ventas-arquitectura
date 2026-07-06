"""Entidad Vehiculo del catálogo."""
from __future__ import annotations

from dataclasses import dataclass

from cotizacion.domain.dinero import Dinero


@dataclass(frozen=True)
class Vehiculo:
    id: str
    marca: str
    modelo: str
    anio: int
    precio_base: Dinero
    disponible: bool = True
