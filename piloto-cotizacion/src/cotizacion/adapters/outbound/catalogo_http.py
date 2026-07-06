"""Adaptador outbound: catálogo vía HTTP (microservicio Catálogo real).

Implementa el MISMO puerto que `ERPCatalogoMock` (`CatalogoPort.obtener`), pero por
detrás hace una llamada de red en lugar de leer memoria. Ni el dominio ni el caso de
uso cambian al pasar del mock a este adaptador: solo se enchufa distinto en `deps.py`.

Actúa además como Anti-Corruption Layer (ACL): traduce el JSON externo al modelo de
dominio `Vehiculo`, de modo que un cambio en el contrato del servicio externo se
absorbe aquí y no se filtra al negocio.
"""
from __future__ import annotations

import httpx

from cotizacion.domain.dinero import Dinero
from cotizacion.domain.vehiculo import Vehiculo


class CatalogoHttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 2.0,
        cliente: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._cliente = cliente or httpx.Client(timeout=timeout)

    def obtener(self, vehiculo_id: str) -> Vehiculo | None:
        url = f"{self._base_url}/vehiculos/{vehiculo_id}"
        respuesta = self._cliente.get(url)
        if respuesta.status_code == httpx.codes.NOT_FOUND:
            return None  # el vehículo no existe (EC-06)
        respuesta.raise_for_status()
        return self._a_dominio(respuesta.json())

    @staticmethod
    def _a_dominio(datos: dict) -> Vehiculo:
        """ACL: contrato externo -> modelo de dominio."""
        return Vehiculo(
            id=datos["id"],
            marca=datos["marca"],
            modelo=datos["modelo"],
            anio=int(datos["anio"]),
            precio_base=Dinero.de(datos["precio_base"]),
            disponible=bool(datos.get("disponible", True)),
        )
