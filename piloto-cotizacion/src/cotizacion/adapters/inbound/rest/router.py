"""Router REST: endpoints de cotización."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from cotizacion.adapters.inbound.rest.deps import get_crear_cotizacion, get_repositorio
from cotizacion.adapters.inbound.rest.schemas import (
    CotizacionResponse,
    CrearCotizacionRequest,
)
from cotizacion.adapters.outbound.repo_memoria import RepositorioMemoria
from cotizacion.application.crear_cotizacion import (
    ComandoCrearCotizacion,
    CrearCotizacion,
    VehiculoNoEncontrado,
)

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])


@router.post("", response_model=CotizacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_cotizacion(
    body: CrearCotizacionRequest,
    caso_uso: CrearCotizacion = Depends(get_crear_cotizacion),
) -> CotizacionResponse:
    comando = ComandoCrearCotizacion(
        vehiculo_id=body.vehiculo_id,
        cliente_id=body.cliente_id,
        clave_idempotencia=body.clave_idempotencia,
    )
    try:
        cotizacion = await caso_uso.ejecutar(comando)
    except VehiculoNoEncontrado as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo no encontrado: {exc}",
        ) from exc
    return CotizacionResponse.desde_dominio(cotizacion)


@router.get("/{cotizacion_id}", response_model=CotizacionResponse)
async def obtener_cotizacion(
    cotizacion_id: str,
    repositorio: RepositorioMemoria = Depends(get_repositorio),
) -> CotizacionResponse:
    cotizacion = repositorio.obtener(cotizacion_id)
    if cotizacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrada")
    return CotizacionResponse.desde_dominio(cotizacion)
