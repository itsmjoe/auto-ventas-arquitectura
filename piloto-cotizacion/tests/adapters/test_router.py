from fastapi.testclient import TestClient

from cotizacion.main import app

cliente = TestClient(app)


def test_crear_cotizacion_exitosa():
    r = cliente.post("/cotizaciones", json={"vehiculo_id": "V-001", "cliente_id": "CLI-1"})
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["moneda"] == "USD"
    assert cuerpo["total"] == "26320.00"
    assert cuerpo["ofertas_financiamiento"]
    # No se filtran datos internos del socio más allá de lo mapeado
    assert set(cuerpo["ofertas_financiamiento"][0].keys()) == {
        "socio",
        "tipo",
        "descripcion",
        "monto_mensual",
    }


def test_body_invalido_devuelve_422():
    r = cliente.post("/cotizaciones", json={"vehiculo_id": "V-001"})
    assert r.status_code == 422


def test_vehiculo_inexistente_devuelve_404():
    r = cliente.post("/cotizaciones", json={"vehiculo_id": "NO-EXISTE", "cliente_id": "CLI-1"})
    assert r.status_code == 404


def test_obtener_cotizacion_por_id():
    creada = cliente.post(
        "/cotizaciones", json={"vehiculo_id": "V-002", "cliente_id": "CLI-9"}
    ).json()
    r = cliente.get(f"/cotizaciones/{creada['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == creada["id"]


def test_obtener_cotizacion_inexistente_devuelve_404():
    r = cliente.get("/cotizaciones/no-existe")
    assert r.status_code == 404


def test_health():
    assert cliente.get("/health").json() == {"status": "ok"}
