"""Adaptador outbound: aseguradora simulada (seguro).

Mismos modos que el banco para ejercitar los edge cases de integración.
"""
from __future__ import annotations

import asyncio
from decimal import Decimal

from cotizacion.domain.cotizacion import Oferta
from cotizacion.domain.vehiculo import Vehiculo


class SocioNoDisponibleError(Exception):
    pass


class AseguradoraMock:
    def __init__(
        self, nombre: str = "Aseguradora Demo", modo: str = "ok", demora: float = 5.0
    ) -> None:
        self._nombre = nombre
        self._modo = modo
        self._demora = demora

    async def cotizar(self, vehiculo: Vehiculo, cliente_id: str) -> list[Oferta]:
        if self._modo == "timeout":
            await asyncio.sleep(self._demora)
        elif self._modo == "caido":
            raise SocioNoDisponibleError(self._nombre)

        # Prima mensual: 3% anual del valor / 12 meses.
        prima = vehiculo.precio_base.multiplicar(Decimal("0.03")).multiplicar(
            Decimal("1") / Decimal("12")
        )
        return [
            Oferta(
                socio=self._nombre,
                tipo="seguro",
                descripcion="Cobertura amplia anual",
                monto_mensual=prima,
            )
        ]
