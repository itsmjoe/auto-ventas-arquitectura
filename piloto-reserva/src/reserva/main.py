"""Punto de entrada FastAPI del microservicio de Reserva."""
from __future__ import annotations

from fastapi import FastAPI

from reserva.adapters.inbound.rest.router import router

app = FastAPI(
    title="Auto Ventas - Piloto de Reserva",
    description="Reserva de vehículos a partir de una cotización vigente.",
    version="0.1.0",
)
app.include_router(router)


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    return {"status": "ok"}
