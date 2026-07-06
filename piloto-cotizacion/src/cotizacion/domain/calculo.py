"""Servicio de dominio: cálculo de impuestos y total de una cotización.

Núcleo puro, sin dependencias de framework. La tasa de impuesto es obligatoria:
una tasa ausente es un error explícito, nunca un impuesto 0 silencioso (EC-11).
"""
from __future__ import annotations

from decimal import Decimal

from cotizacion.domain.dinero import Dinero


class TasaImpuestoInvalida(ValueError):
    """La tasa de impuesto no está configurada o está fuera de rango."""


def validar_tasa(tasa: Decimal | None) -> Decimal:
    if tasa is None:
        raise TasaImpuestoInvalida("La tasa de impuesto no está configurada")
    if tasa < 0 or tasa > 1:
        raise TasaImpuestoInvalida(f"Tasa fuera de rango [0,1]: {tasa}")
    return tasa


def calcular_impuestos(precio_base: Dinero, tasa: Decimal | None) -> Dinero:
    return precio_base.multiplicar(validar_tasa(tasa))


def calcular_total(
    precio_base: Dinero, impuestos: Dinero, descuentos: Dinero | None = None
) -> Dinero:
    subtotal = precio_base.sumar(impuestos)
    if descuentos is not None:
        return subtotal.restar(descuentos)
    return subtotal
