"""DTOs (Pydantic) del adaptador REST. No exponen el modelo de dominio directamente
ni datos internos de los socios (EC-19)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from cotizacion.domain.cotizacion import Cotizacion


class CrearCotizacionRequest(BaseModel):
    vehiculo_id: str = Field(..., min_length=1)
    cliente_id: str = Field(..., min_length=1)
    clave_idempotencia: str | None = None


class OfertaResponse(BaseModel):
    socio: str
    tipo: str
    descripcion: str
    monto_mensual: Decimal


class CotizacionResponse(BaseModel):
    id: str
    vehiculo_id: str
    cliente_id: str
    precio_base: Decimal
    impuestos: Decimal
    total: Decimal
    moneda: str = "USD"
    disponible: bool
    creada_en: datetime
    expira_en: datetime
    ofertas_financiamiento: list[OfertaResponse]
    ofertas_seguro: list[OfertaResponse]
    advertencias: list[str]

    @classmethod
    def desde_dominio(cls, c: Cotizacion) -> CotizacionResponse:
        def mapear(ofertas: list) -> list[OfertaResponse]:
            return [
                OfertaResponse(
                    socio=o.socio,
                    tipo=o.tipo,
                    descripcion=o.descripcion,
                    monto_mensual=o.monto_mensual.monto,
                )
                for o in ofertas
            ]

        return cls(
            id=c.id,
            vehiculo_id=c.vehiculo_id,
            cliente_id=c.cliente_id,
            precio_base=c.precio_base.monto,
            impuestos=c.impuestos.monto,
            total=c.total.monto,
            disponible=c.disponible,
            creada_en=c.creada_en,
            expira_en=c.expira_en,
            ofertas_financiamiento=mapear(c.ofertas_financiamiento),
            ofertas_seguro=mapear(c.ofertas_seguro),
            advertencias=c.advertencias,
        )
