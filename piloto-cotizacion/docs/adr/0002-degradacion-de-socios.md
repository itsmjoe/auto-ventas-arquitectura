# ADR 0002 — Degradación ante fallo de socios

- **Estado:** Aceptado
- **Fecha:** 2026-07-06

## Contexto
La cotización depende de socios externos (bancos, aseguradoras) cuya disponibilidad y
latencia no controlamos. Un fallo de un socio no debe impedir cotizar un vehículo.

## Decisión
Las consultas a socios se ejecutan **en paralelo** (`asyncio.gather`) con **timeout**
por socio (`asyncio.wait_for`). Ante timeout, error o socio caído:
- Se devuelve la cotización **degradada**: solo la parte que sí respondió.
- Si ningún socio responde, se entrega la **cotización base** (precio + impuestos).
- Cada ausencia se refleja en `advertencias` (p. ej. `"financiamiento no disponible"`).
- Las ofertas con datos inconsistentes (monto ≤ 0) se descartan.

## Consecuencias
- **+** La cotización nunca se bloquea por un tercero (EC-01, EC-02, EC-03, EC-21).
- **+** El consumidor sabe explícitamente qué faltó vía `advertencias`.
- **−** El cliente puede recibir una cotización sin financiamiento/seguro; es preferible
  a un error total. En producción se complementaría con **circuit breaker** y reintentos
  idempotentes.
