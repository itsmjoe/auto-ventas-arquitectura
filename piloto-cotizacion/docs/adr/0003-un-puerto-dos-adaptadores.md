# ADR 0003 — Un puerto, dos adaptadores para el catálogo

- **Estado:** Aceptado
- **Fecha:** 2026-07-06

## Contexto
El caso de uso necesita datos del vehículo. Hoy (piloto) esos datos son simulados; en la
arquitectura objetivo vendrán del microservicio **Catálogo** por la red. Queremos poder
migrar de uno a otro sin reescribir la lógica de negocio, y demostrarlo de forma tangible.

## Decisión
Definimos un único puerto `CatalogoPort.obtener(vehiculo_id) -> Vehiculo | None` con **dos
implementaciones**:
- `ERPCatalogoMock`: lectura en memoria (por defecto).
- `CatalogoHttpClient`: llamada HTTP a un microservicio; traduce el JSON externo al
  modelo de dominio (Anti-Corruption Layer).

La selección es por configuración (`COTIZACION_CATALOGO_URL`) y ocurre en `deps.py`, el
único lugar que conoce implementaciones concretas.

## Consecuencias
- **+** Pasar de mock a microservicio real = enchufar otro adaptador; dominio y caso de
  uso intactos (probado en `tests/adapters/test_catalogo_http.py`).
- **+** El contrato externo queda aislado en el adaptador (ACL): un cambio de esquema no
  se filtra al negocio.
- **−** El puerto es síncrono; el adaptador HTTP usa un cliente síncrono. Para alta
  concurrencia se migraría a un puerto asíncrono (cambio localizado en puerto + adaptadores,
  no en el dominio).
- **Nota:** ante caída del servicio de catálogo, en producción se mapearía el error a
  `503`; en el piloto el error de red se propaga sin manejo específico.
