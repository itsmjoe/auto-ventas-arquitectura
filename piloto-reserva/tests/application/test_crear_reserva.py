from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from reserva.adapters.outbound.cotizacion_mock import CotizacionMock
from reserva.adapters.outbound.repo_memoria import RepositorioMemoria
from reserva.application.crear_reserva import (
    ComandoCrearReserva,
    CotizacionExpirada,
    CotizacionNoEncontrada,
    CrearReserva,
    VehiculoNoDisponible,
)
from reserva.application.ports import CotizacionInfo
from reserva.domain.reserva import EstadoReserva

RELOJ = datetime(2026, 7, 6, 12, 0, 0, tzinfo=UTC)


def _info(disponible=True, minutos_vigencia=60):
    return CotizacionInfo(
        id="COT-1",
        vehiculo_id="V-001",
        total=Decimal("26320.00"),
        disponible=disponible,
        expira_en=RELOJ + timedelta(minutes=minutos_vigencia),
    )


def _caso(info=None):
    cotizaciones = CotizacionMock({"COT-1": info} if info else {})
    return CrearReserva(
        cotizaciones=cotizaciones,
        repositorio=RepositorioMemoria(),
        reloj=lambda: RELOJ,
        generador_id=lambda: "RES-1",
    )


def test_reserva_exitosa_de_cotizacion_vigente_disponible():
    reserva = _caso(_info()).ejecutar(ComandoCrearReserva("COT-1", "CLI-1"))
    assert reserva.estado is EstadoReserva.CONFIRMADA
    assert reserva.vehiculo_id == "V-001"


def test_cotizacion_inexistente():
    with pytest.raises(CotizacionNoEncontrada):
        _caso().ejecutar(ComandoCrearReserva("NO-EXISTE", "CLI-1"))


def test_cotizacion_expirada_obliga_a_recotizar():
    with pytest.raises(CotizacionExpirada):
        _caso(_info(minutos_vigencia=-1)).ejecutar(ComandoCrearReserva("COT-1", "CLI-1"))


def test_vehiculo_no_disponible():
    with pytest.raises(VehiculoNoDisponible):
        _caso(_info(disponible=False)).ejecutar(ComandoCrearReserva("COT-1", "CLI-1"))
