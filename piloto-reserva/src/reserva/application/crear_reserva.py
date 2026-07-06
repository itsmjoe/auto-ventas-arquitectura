"""Caso de uso: CrearReserva.

Reglas de negocio antes de reservar:
- La cotización debe existir.
- Debe estar VIGENTE; si expiró, se obliga a recotizar (EC-14).
- El vehículo debe estar DISPONIBLE (EC-07 / EC-15).

Nota (EC-15): en producción el ERP es el system of record y confirma la reserva; aquí
el servicio la registra como CONFIRMADA para el piloto.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from reserva.application.ports import CotizacionPort, ReservaRepositoryPort
from reserva.domain.reserva import EstadoReserva, Reserva


class CotizacionNoEncontrada(Exception):
    pass


class CotizacionExpirada(Exception):
    pass


class VehiculoNoDisponible(Exception):
    pass


@dataclass(frozen=True)
class ComandoCrearReserva:
    cotizacion_id: str
    cliente_id: str


def _ahora_utc() -> datetime:
    return datetime.now(UTC)


class CrearReserva:
    def __init__(
        self,
        cotizaciones: CotizacionPort,
        repositorio: ReservaRepositoryPort,
        reloj: Callable[[], datetime] = _ahora_utc,
        generador_id: Callable[[], str] = lambda: str(uuid4()),
    ) -> None:
        self._cotizaciones = cotizaciones
        self._repositorio = repositorio
        self._reloj = reloj
        self._generar_id = generador_id

    def ejecutar(self, comando: ComandoCrearReserva) -> Reserva:
        info = self._cotizaciones.obtener(comando.cotizacion_id)
        if info is None:
            raise CotizacionNoEncontrada(comando.cotizacion_id)

        ahora = self._reloj()
        if ahora >= info.expira_en:
            raise CotizacionExpirada(comando.cotizacion_id)
        if not info.disponible:
            raise VehiculoNoDisponible(info.vehiculo_id)

        reserva = Reserva(
            id=self._generar_id(),
            cotizacion_id=info.id,
            vehiculo_id=info.vehiculo_id,
            cliente_id=comando.cliente_id,
            estado=EstadoReserva.CONFIRMADA,
            creada_en=ahora,
        )
        self._repositorio.guardar(reserva)
        return reserva
