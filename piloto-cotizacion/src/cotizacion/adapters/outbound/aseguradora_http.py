"""Adaptador outbound: aseguradora real vía HTTP (seguro).

Implementa el MISMO puerto que `AseguradoraMock` (`SeguroPort.cotizar`).
"""
from __future__ import annotations

import httpx

from cotizacion.domain.cotizacion import Oferta
from cotizacion.domain.dinero import Dinero
from cotizacion.domain.vehiculo import Vehiculo


class AseguradoraHttpClient:
    def __init__(
        self,
        base_url: str,
        nombre: str = "Aseguradora",
        timeout: float = 2.0,
        cliente: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._nombre = nombre
        self._timeout = timeout
        self._cliente = cliente

    async def cotizar(self, vehiculo: Vehiculo, cliente_id: str) -> list[Oferta]:
        payload = {
            "vehiculo_id": vehiculo.id,
            "precio_base": str(vehiculo.precio_base.monto),
            "cliente_id": cliente_id,
        }
        url = f"{self._base_url}/seguro"
        if self._cliente is not None:
            respuesta = await self._cliente.post(url, json=payload)
        else:
            async with httpx.AsyncClient(timeout=self._timeout) as cliente:
                respuesta = await cliente.post(url, json=payload)
        respuesta.raise_for_status()
        return [self._a_oferta(o) for o in respuesta.json().get("ofertas", [])]

    def _a_oferta(self, datos: dict) -> Oferta:
        return Oferta(
            socio=datos.get("socio", self._nombre),
            tipo="seguro",
            descripcion=datos["descripcion"],
            monto_mensual=Dinero.de(datos["monto_mensual"]),
        )
