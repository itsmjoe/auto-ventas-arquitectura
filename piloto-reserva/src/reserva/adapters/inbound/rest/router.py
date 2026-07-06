"""Router REST de Reserva."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from reserva.adapters.inbound.rest.deps import get_crear_reserva, get_repositorio
from reserva.adapters.inbound.rest.schemas import CrearReservaRequest, ReservaResponse
from reserva.adapters.outbound.repo_memoria import RepositorioMemoria
from reserva.application.crear_reserva import (
    ComandoCrearReserva,
    CotizacionExpirada,
    CotizacionNoEncontrada,
    CrearReserva,
    VehiculoNoDisponible,
)

router = APIRouter(prefix="/reservas", tags=["reservas"])


@router.post("", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
def crear_reserva(
    body: CrearReservaRequest,
    caso_uso: CrearReserva = Depends(get_crear_reserva),
) -> ReservaResponse:
    comando = ComandoCrearReserva(cotizacion_id=body.cotizacion_id, cliente_id=body.cliente_id)
    try:
        reserva = caso_uso.ejecutar(comando)
    except CotizacionNoEncontrada as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cotización no encontrada") from exc
    except CotizacionExpirada as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cotización expirada, recotice") from exc
    except VehiculoNoDisponible as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Vehículo no disponible") from exc
    return ReservaResponse.desde_dominio(reserva)


@router.get("/{reserva_id}", response_model=ReservaResponse)
def obtener_reserva(
    reserva_id: str,
    repositorio: RepositorioMemoria = Depends(get_repositorio),
) -> ReservaResponse:
    reserva = repositorio.obtener(reserva_id)
    if reserva is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reserva no encontrada")
    return ReservaResponse.desde_dominio(reserva)
