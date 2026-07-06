# Piloto — Reserva de vehículos (Auto Ventas)

Segundo microservicio del portal. Reserva un vehículo **a partir de una cotización**, y
para ello **llama al microservicio de Cotización** por HTTP. Es la demostración de
**dos hexágonos comunicándose**.

## Arquitectura (hexagonal)

```
src/reserva/
├── domain/        # entidad Reserva, EstadoReserva
├── application/   # caso de uso CrearReserva + puertos (CotizacionPort, RepositoryPort)
└── adapters/
    ├── inbound/rest/   # API FastAPI
    └── outbound/       # CotizacionHttpClient (llama a Cotización) / mock / repo
```

### Cómo hablan los dos servicios
`CrearReserva` necesita datos de la cotización → los pide por el puerto `CotizacionPort`.
Detrás hay dos adaptadores intercambiables:
- `CotizacionMock` — en memoria (tests / local sin el otro servicio).
- `CotizacionHttpClient` — `GET http://cotizacion-svc/cotizaciones/{id}` y traduce la
  respuesta al modelo `CotizacionInfo` (Anti-Corruption Layer).

Se elige por `RESERVA_COTIZACION_URL`. Reserva **no conoce** el esquema interno de
Cotización: solo el contrato del puerto.

## Reglas de negocio (edge cases)
- La cotización debe **existir** → `404`.
- Debe estar **vigente**; si expiró → `409` (recotice) (EC-14).
- El vehículo debe estar **disponible** → `409` (EC-07 / EC-15).
- Nota (EC-15): en producción el **ERP** es el system of record y confirma la reserva;
  aquí el servicio la registra como `CONFIRMADA` para el piloto.

## Cómo correr
```bash
pip install -e ".[dev]"
# apuntar al servicio de Cotización (ver más abajo el demo end-to-end)
export RESERVA_COTIZACION_URL=http://localhost:8000
uvicorn reserva.main:app --port 8001
```

## API
- `POST /reservas` → `{ "cotizacion_id": "...", "cliente_id": "..." }` → `201`
- `GET /reservas/{id}` → `200` / `404`

## Tests
```bash
pytest -q
ruff check .
```
