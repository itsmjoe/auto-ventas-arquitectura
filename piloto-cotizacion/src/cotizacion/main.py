"""Punto de entrada FastAPI del piloto de cotización."""
from __future__ import annotations

from fastapi import FastAPI

from cotizacion.adapters.inbound.rest.router import router

app = FastAPI(
    title="Auto Ventas - Piloto de Cotización",
    description="Cotización de vehículos en USD con integración simulada de banco y aseguradora.",
    version="0.1.0",
)
app.include_router(router)


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    return {"status": "ok"}
