# Piloto — Cotización de vehículos (Auto Ventas)

Microservicio que cotiza un vehículo en **USD** (precio base + impuestos) e integra, de
forma resiliente, ofertas de **financiamiento** (banco) y **seguro** (aseguradora).
Es el piloto del caso práctico de arquitectura; las integraciones externas están
**simuladas** mediante adaptadores mock que permiten ejercitar los edge cases.

## Arquitectura (hexagonal)

```
src/cotizacion/
├── domain/        # entidades y reglas puras (Dinero, Vehiculo, Cotizacion, cálculo)
├── application/   # casos de uso + puertos (interfaces)
└── adapters/
    ├── inbound/rest/   # API FastAPI
    └── outbound/       # ERP mock + catálogo HTTP + banco / aseguradora / repositorio
```

### Un puerto, dos adaptadores (mock ↔ microservicio real)
El catálogo se consume por el puerto `CatalogoPort`. Detrás hay dos adaptadores
intercambiables **sin tocar dominio ni caso de uso**:
- `ERPCatalogoMock` — datos en memoria (por defecto).
- `CatalogoHttpClient` — llama a un microservicio real por HTTP (y traduce su JSON al
  modelo de dominio: Anti-Corruption Layer).

Se elige por configuración: si defines `COTIZACION_CATALOGO_URL`, se usa el adaptador
HTTP; si no, el mock. Ver `deps.py`. Es la demostración concreta de cómo hexagonal deja
pasar de "monolito con mock" a "microservicio en red" cambiando solo el enchufe.

- El **dominio** no depende de ningún framework.
- Los **casos de uso** dependen de **puertos**; los **adaptadores** los implementan.
- Sustituir un mock por una integración real (ERP, RDS, API de un banco) no toca el dominio.

Ver decisiones en [`docs/adr/`](docs/adr).

## Requisitos
- Python 3.11+ (imagen Docker usa 3.12).

## Cómo correr

### Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn cotizacion.main:app --reload
```
Documentación interactiva (OpenAPI/Swagger): http://localhost:8000/docs

### Docker
```bash
docker compose up --build
```

## Tests y lint
```bash
pytest -q
ruff check .
```

## API

### `POST /cotizaciones`
```json
{ "vehiculo_id": "V-001", "cliente_id": "CLI-1", "clave_idempotencia": "opcional" }
```
Respuesta `201`:
```json
{
  "id": "…",
  "precio_base": "23500.00",
  "impuestos": "2820.00",
  "total": "26320.00",
  "moneda": "USD",
  "disponible": true,
  "ofertas_financiamiento": [{ "socio": "Banco Demo", "tipo": "financiamiento", "descripcion": "48 meses, 8% anual", "monto_mensual": "528.75" }],
  "ofertas_seguro": [ ... ],
  "advertencias": []
}
```
- `422` si el body es inválido.
- `404` si el vehículo no existe.

### `GET /cotizaciones/{id}`
Devuelve una cotización previamente creada (`404` si no existe).

## Catálogo de prueba
| ID | Vehículo | Precio base | Disponible |
|----|----------|-------------|------------|
| V-001 | Toyota Corolla 2024 | 23 500.00 | sí |
| V-002 | Mazda CX-5 2024 | 31 200.00 | sí |
| V-003 | Nissan Frontier 2023 | 38 900.00 | no (se cotiza, no se reserva) |

## Edge cases cubiertos
Se controlan vía variables de entorno `COTIZACION_MODO_BANCO` / `COTIZACION_MODO_ASEGURADORA`
(`ok` | `timeout` | `caido`) y están cubiertos por tests:

- **Degradación de socios:** timeout / caído → cotización parcial o solo base, con `advertencias`.
- **Vehículo inexistente** → `404`; **vehículo sin stock** → se cotiza con `disponible: false`.
- **Dinero con `Decimal`** y redondeo bancario; descuentos acotados a 0.
- **Tasa de impuesto** ausente/ inválida → error explícito.
- **Idempotencia** por clave: doble envío devuelve la misma cotización.
- **No se filtran** datos internos de los socios en la respuesta.

## Configuración
Ver [`.env.example`](.env.example). Todo se configura por entorno; no hay secretos en el código.
