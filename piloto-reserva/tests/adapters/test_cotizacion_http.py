from decimal import Decimal

import httpx

from reserva.adapters.outbound.cotizacion_http import CotizacionHttpClient

COT_JSON = {
    "id": "COT-1",
    "vehiculo_id": "V-001",
    "total": "26320.00",
    "disponible": True,
    "expira_en": "2026-07-06T13:00:00+00:00",
}


def _cliente_falso() -> httpx.Client:
    def manejar(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cotizaciones/COT-1":
            return httpx.Response(200, json=COT_JSON)
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(manejar))


def test_traduce_cotizacion_del_servicio():
    adaptador = CotizacionHttpClient("http://cotizacion-svc", cliente=_cliente_falso())
    info = adaptador.obtener("COT-1")
    assert info is not None
    assert info.vehiculo_id == "V-001"
    assert info.total == Decimal("26320.00")
    assert info.expira_en.year == 2026


def test_devuelve_none_si_no_existe():
    adaptador = CotizacionHttpClient("http://cotizacion-svc", cliente=_cliente_falso())
    assert adaptador.obtener("NO-EXISTE") is None
