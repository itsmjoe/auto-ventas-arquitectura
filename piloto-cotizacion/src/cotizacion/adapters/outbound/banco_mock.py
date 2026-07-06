"""Adaptador outbound: banco simulado (financiamiento).

Parametrizable por modo para poder ejercitar los edge cases de integración:
- "ok": devuelve ofertas de financiamiento.
- "timeout": tarda más que el timeout del caso de uso (EC-01).
- "caido": lanza excepción, simulando socio no disponible (EC-02).
"""
from __future__ import annotations

import asyncio
from decimal import Decimal

from cotizacion.domain.cotizacion import Oferta
from cotizacion.domain.vehiculo import Vehiculo


class SocioNoDisponibleError(Exception):
    pass


class BancoMock:
    def __init__(self, nombre: str = "Banco Demo", modo: str = "ok", demora: float = 5.0) -> None:
        self._nombre = nombre
        self._modo = modo
        self._demora = demora

    async def cotizar(self, vehiculo: Vehiculo, cliente_id: str) -> list[Oferta]:
        if self._modo == "timeout":
            await asyncio.sleep(self._demora)
        elif self._modo == "caido":
            raise SocioNoDisponibleError(self._nombre)

        # Cuota mensual simple: (precio + 8% interés) / 48 meses.
        total_con_interes = vehiculo.precio_base.multiplicar(Decimal("1.08"))
        cuota = total_con_interes.multiplicar(Decimal("1") / Decimal("48"))
        return [
            Oferta(
                socio=self._nombre,
                tipo="financiamiento",
                descripcion="48 meses, 8% anual",
                monto_mensual=cuota,
            )
        ]
