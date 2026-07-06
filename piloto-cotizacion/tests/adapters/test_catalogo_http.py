"""Demuestra que el MISMO puerto (CatalogoPort) sirve a dos mundos:
el mock en memoria y un microservicio real por HTTP. El dominio y el caso de uso
no cambian; solo cambia el adaptador que se enchufa.
"""
from decimal import Decimal

import httpx

from cotizacion.adapters.outbound.aseguradora_mock import AseguradoraMock
from cotizacion.adapters.outbound.banco_mock import BancoMock
from cotizacion.adapters.outbound.catalogo_http import CatalogoHttpClient
from cotizacion.adapters.outbound.repo_memoria import RepositorioMemoria
from cotizacion.application.crear_cotizacion import ComandoCrearCotizacion, CrearCotizacion

VEHICULO_JSON = {
    "id": "V-001",
    "marca": "Toyota",
    "modelo": "Corolla",
    "anio": 2024,
    "precio_base": "23500.00",
    "disponible": True,
}


def _cliente_http_falso() -> httpx.Client:
    """Cliente httpx que responde sin tocar la red (MockTransport)."""

    def manejar(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/vehiculos/V-001":
            return httpx.Response(200, json=VEHICULO_JSON)
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(manejar))


def test_adaptador_http_traduce_json_a_dominio():
    adaptador = CatalogoHttpClient("http://catalogo-svc", cliente=_cliente_http_falso())
    vehiculo = adaptador.obtener("V-001")
    assert vehiculo is not None
    assert vehiculo.marca == "Toyota"
    assert vehiculo.precio_base.monto == Decimal("23500.00")


def test_adaptador_http_devuelve_none_si_404():
    adaptador = CatalogoHttpClient("http://catalogo-svc", cliente=_cliente_http_falso())
    assert adaptador.obtener("NO-EXISTE") is None


async def test_mismo_caso_de_uso_funciona_con_catalogo_http():
    # Se cambia SOLO el adaptador de catálogo (mock -> HTTP). Todo lo demás igual.
    caso = CrearCotizacion(
        catalogo=CatalogoHttpClient("http://catalogo-svc", cliente=_cliente_http_falso()),
        financiamiento=BancoMock(),
        seguro=AseguradoraMock(),
        repositorio=RepositorioMemoria(),
        tasa_impuesto=Decimal("0.12"),
    )
    cot = await caso.ejecutar(ComandoCrearCotizacion("V-001", "CLI-1"))
    # Mismo resultado de negocio que con el mock: base 23500 + 12% = 26320.
    assert cot.total.monto == Decimal("26320.00")
    assert cot.ofertas_financiamiento and cot.ofertas_seguro
