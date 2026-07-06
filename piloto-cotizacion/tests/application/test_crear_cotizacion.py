from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cotizacion.adapters.outbound.aseguradora_mock import AseguradoraMock
from cotizacion.adapters.outbound.banco_mock import BancoMock
from cotizacion.adapters.outbound.erp_catalogo_mock import ERPCatalogoMock
from cotizacion.adapters.outbound.repo_memoria import RepositorioMemoria
from cotizacion.application.crear_cotizacion import (
    ComandoCrearCotizacion,
    CrearCotizacion,
    VehiculoNoEncontrado,
)

RELOJ_FIJO = datetime(2026, 7, 6, 12, 0, 0, tzinfo=UTC)


def construir(modo_banco="ok", modo_aseguradora="ok", repositorio=None):
    ids = iter(f"COT-{i}" for i in range(1, 100))
    return CrearCotizacion(
        catalogo=ERPCatalogoMock(),
        financiamiento=BancoMock(modo=modo_banco),
        seguro=AseguradoraMock(modo=modo_aseguradora),
        repositorio=repositorio or RepositorioMemoria(),
        tasa_impuesto=Decimal("0.12"),
        timeout_socios=0.05,
        reloj=lambda: RELOJ_FIJO,
        generador_id=lambda: next(ids),
    )


async def test_happy_path_cotiza_con_impuestos_y_ofertas():
    caso = construir()
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-001", "CLI-1"))

    assert cot.precio_base.monto == Decimal("23500.00")
    assert cot.impuestos.monto == Decimal("2820.00")  # 12%
    assert cot.total.monto == Decimal("26320.00")
    assert cot.ofertas_financiamiento and cot.ofertas_seguro
    assert cot.advertencias == []
    assert cot.disponible is True


async def test_vehiculo_inexistente_lanza_error():
    caso = construir()
    with pytest.raises(VehiculoNoEncontrado):
        await caso.ejecutar(ComandoCrearCotizacion("NO-EXISTE", "CLI-1"))


async def test_banco_timeout_degrada_solo_financiamiento():
    caso = construir(modo_banco="timeout")
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-001", "CLI-1"))

    assert cot.ofertas_financiamiento == []
    assert cot.ofertas_seguro  # el seguro sí responde
    assert "financiamiento no disponible" in cot.advertencias
    assert cot.total.monto == Decimal("26320.00")  # la cotización base no se afecta


async def test_aseguradora_caida_degrada_solo_seguro():
    caso = construir(modo_aseguradora="caido")
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-001", "CLI-1"))

    assert cot.ofertas_seguro == []
    assert cot.ofertas_financiamiento
    assert "seguro no disponible" in cot.advertencias


async def test_degradacion_total_devuelve_solo_cotizacion_base():
    caso = construir(modo_banco="caido", modo_aseguradora="caido")
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-001", "CLI-1"))

    assert cot.ofertas_financiamiento == []
    assert cot.ofertas_seguro == []
    assert set(cot.advertencias) == {"financiamiento no disponible", "seguro no disponible"}
    assert cot.total.monto == Decimal("26320.00")


async def test_vehiculo_sin_stock_se_cotiza_pero_marca_no_disponible():
    caso = construir()
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-003", "CLI-1"))
    assert cot.disponible is False  # existe pero no disponible (EC-07)


async def test_idempotencia_devuelve_la_misma_cotizacion():
    repo = RepositorioMemoria()
    caso = construir(repositorio=repo)
    cmd = ComandoCrearCotizacion("V-001", "CLI-1", clave_idempotencia="abc-123")

    primera = await caso.ejecutar(cmd)
    segunda = await caso.ejecutar(cmd)
    assert primera.id == segunda.id
