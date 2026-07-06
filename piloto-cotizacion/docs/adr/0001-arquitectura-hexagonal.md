# ADR 0001 — Arquitectura hexagonal para el piloto

- **Estado:** Aceptado
- **Fecha:** 2026-07-06

## Contexto
El piloto de cotización debe integrarse con múltiples sistemas externos (ERP, bancos,
aseguradoras, base de datos) que en el piloto son simulados y en producción serán
reales. Necesitamos poder sustituir esas integraciones sin reescribir la lógica de negocio.

## Decisión
Adoptamos **arquitectura hexagonal (puertos y adaptadores)**:
- `domain/`: entidades y reglas puras, sin dependencias de framework.
- `application/`: casos de uso que dependen de **puertos** (interfaces).
- `adapters/inbound/`: API REST (FastAPI).
- `adapters/outbound/`: implementaciones concretas (mocks hoy, ERP/RDS/APIs mañana).

## Consecuencias
- **+** El dominio es testeable sin infraestructura y no conoce a los socios.
- **+** Sustituir un mock por una integración real no toca dominio ni casos de uso.
- **−** Más archivos/indirección que un CRUD monolítico; se justifica por el objetivo
  de integración de la solución.
