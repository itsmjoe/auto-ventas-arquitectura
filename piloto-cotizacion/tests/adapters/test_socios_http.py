"""Adaptadores HTTP de socios (banco y aseguradora) sobre el mismo puerto que los mocks."""
from decimal import Decimal

import httpx

from cotizacion.adapters.outbound.aseguradora_http import AseguradoraHttpClient
from cotizacion.adapters.outbound.aseguradora_mock import AseguradoraMock
from cotizacion.adapters.outbound.banco_http import BancoHttpClient
from cotizacion.adapters.outbound.erp_catalogo_mock import ERPCatalogoMock
from cotizacion.adapters.outbound.repo_memoria import RepositorioMemoria
from cotizacion.application.crear_cotizacion import ComandoCrearCotizacion, CrearCotizacion
from cotizacion.domain.dinero import Dinero
from cotizacion.domain.vehiculo import Vehiculo

VEHICULO = Vehiculo("V-001", "Toyota", "Corolla", 2024, Dinero.de("23500.00"), True)


def _cliente_banco_ok() -> httpx.AsyncClient:
    oferta = {"socio": "Banco X", "descripcion": "48m", "monto_mensual": "500.00"}

    def manejar(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ofertas": [oferta]})

    return httpx.AsyncClient(transport=httpx.MockTransport(manejar))


def _cliente_caido() -> httpx.AsyncClient:
    def manejar(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    return httpx.AsyncClient(transport=httpx.MockTransport(manejar))


async def test_banco_http_traduce_ofertas():
    banco = BancoHttpClient("http://banco-svc", cliente=_cliente_banco_ok())
    ofertas = await banco.cotizar(VEHICULO, "CLI-1")
    assert len(ofertas) == 1
    assert ofertas[0].tipo == "financiamiento"
    assert ofertas[0].monto_mensual.monto == Decimal("500.00")


async def test_caso_de_uso_con_banco_http_ok():
    caso = CrearCotizacion(
        catalogo=ERPCatalogoMock(),
        financiamiento=BancoHttpClient("http://banco-svc", cliente=_cliente_banco_ok()),
        seguro=AseguradoraMock(),
        repositorio=RepositorioMemoria(),
        tasa_impuesto=Decimal("0.12"),
    )
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-001", "CLI-1"))
    assert cot.total.monto == Decimal("26320.00")
    assert cot.ofertas_financiamiento[0].monto_mensual.monto == Decimal("500.00")


async def test_banco_http_caido_degrada_igual_que_el_mock():
    # La resiliencia del caso de uso funciona idéntica con un adaptador HTTP real.
    caso = CrearCotizacion(
        catalogo=ERPCatalogoMock(),
        financiamiento=BancoHttpClient("http://banco-svc", cliente=_cliente_caido()),
        seguro=AseguradoraMock(),
        repositorio=RepositorioMemoria(),
        tasa_impuesto=Decimal("0.12"),
    )
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-001", "CLI-1"))
    assert cot.ofertas_financiamiento == []
    assert "financiamiento no disponible" in cot.advertencias
    assert cot.total.monto == Decimal("26320.00")


async def test_aseguradora_http_traduce_ofertas():
    def manejar(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"ofertas": [{"descripcion": "amplia", "monto_mensual": "60.00"}]},
        )

    aseg = AseguradoraHttpClient(
        "http://aseg-svc", cliente=httpx.AsyncClient(transport=httpx.MockTransport(manejar))
    )
    ofertas = await aseg.cotizar(VEHICULO, "CLI-1")
    assert ofertas[0].tipo == "seguro"
    assert ofertas[0].monto_mensual.monto == Decimal("60.00")
