"""Adaptador outbound: catálogo simulado del ERP.

Representa la lectura de inventario que en producción vendría del ERP vía ACL /
réplica de solo lectura. Aquí es un catálogo fijo en memoria.
"""
from __future__ import annotations

from cotizacion.domain.dinero import Dinero
from cotizacion.domain.vehiculo import Vehiculo

_CATALOGO: dict[str, Vehiculo] = {
    "V-001": Vehiculo("V-001", "Toyota", "Corolla", 2024, Dinero.de("23500.00"), True),
    "V-002": Vehiculo("V-002", "Mazda", "CX-5", 2024, Dinero.de("31200.00"), True),
    "V-003": Vehiculo("V-003", "Nissan", "Frontier", 2023, Dinero.de("38900.00"), False),
}


class ERPCatalogoMock:
    def __init__(self, catalogo: dict[str, Vehiculo] | None = None) -> None:
        self._catalogo = catalogo if catalogo is not None else dict(_CATALOGO)

    def obtener(self, vehiculo_id: str) -> Vehiculo | None:
        return self._catalogo.get(vehiculo_id)
