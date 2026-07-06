"""Entidades Cotizacion y Oferta (resultado de socios)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from cotizacion.domain.dinero import Dinero


@dataclass(frozen=True)
class Oferta:
    """Oferta de un socio (financiamiento de banco o seguro de aseguradora)."""

    socio: str
    tipo: str  # "financiamiento" | "seguro"
    descripcion: str
    monto_mensual: Dinero


@dataclass(frozen=True)
class Cotizacion:
    id: str
    vehiculo_id: str
    cliente_id: str
    precio_base: Dinero
    impuestos: Dinero
    total: Dinero
    disponible: bool
    creada_en: datetime
    expira_en: datetime
    ofertas_financiamiento: list[Oferta] = field(default_factory=list)
    ofertas_seguro: list[Oferta] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    def esta_vigente(self, ahora: datetime) -> bool:
        """Una cotización expirada obliga a recotizar antes de reservar (EC-14)."""
        return ahora < self.expira_en
