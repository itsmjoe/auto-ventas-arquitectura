from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient

from reserva.adapters.inbound.rest.deps import get_crear_reserva, get_repositorio
from reserva.adapters.outbound.cotizacion_mock import CotizacionMock
from reserva.adapters.outbound.repo_memoria import RepositorioMemoria
from reserva.application.crear_reserva import CrearReserva
from reserva.application.ports import CotizacionInfo
from reserva.main import app

RELOJ = datetime(2026, 7, 6, 12, 0, 0, tzinfo=UTC)


def _caso_con_cotizacion_vigente() -> CrearReserva:
    info = CotizacionInfo(
        id="COT-1",
        vehiculo_id="V-001",
        total=Decimal("26320.00"),
        disponible=True,
        expira_en=RELOJ + timedelta(hours=1),
    )
    return CrearReserva(
        cotizaciones=CotizacionMock({"COT-1": info}),
        repositorio=_repo,
        reloj=lambda: RELOJ,
    )


_repo = RepositorioMemoria()
app.dependency_overrides[get_crear_reserva] = _caso_con_cotizacion_vigente
app.dependency_overrides[get_repositorio] = lambda: _repo

cliente = TestClient(app)


def test_crear_reserva_exitosa():
    r = cliente.post("/reservas", json={"cotizacion_id": "COT-1", "cliente_id": "CLI-1"})
    assert r.status_code == 201
    assert r.json()["estado"] == "CONFIRMADA"


def test_body_invalido_422():
    r = cliente.post("/reservas", json={"cotizacion_id": "COT-1"})
    assert r.status_code == 422


def test_cotizacion_inexistente_404():
    r = cliente.post("/reservas", json={"cotizacion_id": "NADA", "cliente_id": "CLI-1"})
    assert r.status_code == 404


def test_obtener_reserva_creada():
    creada = cliente.post(
        "/reservas", json={"cotizacion_id": "COT-1", "cliente_id": "CLI-2"}
    ).json()
    r = cliente.get(f"/reservas/{creada['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == creada["id"]
