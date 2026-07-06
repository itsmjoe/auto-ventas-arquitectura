"""Caso de uso: CrearCotizacion.

Orquesta el cálculo de precio + impuestos y consulta a los socios (banco y
aseguradora) EN PARALELO con timeout. Si un socio falla o tarda, la cotización
se devuelve de forma degradada (parcial o solo base) — nunca se bloquea
(EC-01, EC-02, EC-03, EC-21). Es idempotente por clave (EC-13).
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from cotizacion.application.ports import (
    CatalogoPort,
    CotizacionRepositoryPort,
    FinanciamientoPort,
    SeguroPort,
)
from cotizacion.domain import calculo
from cotizacion.domain.cotizacion import Cotizacion, Oferta


class VehiculoNoEncontrado(Exception):
    """El vehículo solicitado no existe en el catálogo (EC-06)."""


@dataclass(frozen=True)
class ComandoCrearCotizacion:
    vehiculo_id: str
    cliente_id: str
    clave_idempotencia: str | None = None


def _ahora_utc() -> datetime:
    return datetime.now(UTC)


class CrearCotizacion:
    def __init__(
        self,
        catalogo: CatalogoPort,
        financiamiento: FinanciamientoPort,
        seguro: SeguroPort,
        repositorio: CotizacionRepositoryPort,
        tasa_impuesto: Decimal,
        vigencia_minutos: int = 60,
        timeout_socios: float = 2.0,
        reloj: Callable[[], datetime] = _ahora_utc,
        generador_id: Callable[[], str] = lambda: str(uuid4()),
    ) -> None:
        self._catalogo = catalogo
        self._financiamiento = financiamiento
        self._seguro = seguro
        self._repositorio = repositorio
        # Se valida al construir: una tasa inválida es error de configuración (EC-11).
        self._tasa = calculo.validar_tasa(tasa_impuesto)
        self._vigencia = timedelta(minutes=vigencia_minutos)
        self._timeout = timeout_socios
        self._reloj = reloj
        self._generar_id = generador_id

    async def ejecutar(self, comando: ComandoCrearCotizacion) -> Cotizacion:
        # Idempotencia: mismo comando repetido devuelve la misma cotización (EC-13).
        if comando.clave_idempotencia:
            existente = self._repositorio.buscar_por_idempotencia(comando.clave_idempotencia)
            if existente is not None:
                return existente

        vehiculo = self._catalogo.obtener(comando.vehiculo_id)
        if vehiculo is None:
            raise VehiculoNoEncontrado(comando.vehiculo_id)

        impuestos = calculo.calcular_impuestos(vehiculo.precio_base, self._tasa)
        total = calculo.calcular_total(vehiculo.precio_base, impuestos)

        # Socios consultados en paralelo; cada fallo degrada solo su parte.
        (fin_ofertas, fin_adv), (seg_ofertas, seg_adv) = await asyncio.gather(
            self._consultar_socio(
                self._financiamiento.cotizar(vehiculo, comando.cliente_id),
                "financiamiento",
            ),
            self._consultar_socio(
                self._seguro.cotizar(vehiculo, comando.cliente_id),
                "seguro",
            ),
        )
        advertencias = [a for a in (fin_adv, seg_adv) if a]

        ahora = self._reloj()
        cotizacion = Cotizacion(
            id=self._generar_id(),
            vehiculo_id=vehiculo.id,
            cliente_id=comando.cliente_id,
            precio_base=vehiculo.precio_base,
            impuestos=impuestos,
            total=total,
            disponible=vehiculo.disponible,
            creada_en=ahora,
            expira_en=ahora + self._vigencia,
            ofertas_financiamiento=fin_ofertas,
            ofertas_seguro=seg_ofertas,
            advertencias=advertencias,
        )
        self._repositorio.guardar(cotizacion, comando.clave_idempotencia)
        return cotizacion

    async def _consultar_socio(
        self, tarea: Awaitable[list[Oferta]], etiqueta: str
    ) -> tuple[list[Oferta], str | None]:
        """Ejecuta la consulta con timeout; ante cualquier fallo devuelve degradado."""
        try:
            ofertas = await asyncio.wait_for(tarea, timeout=self._timeout)
        except Exception:  # timeout, socio caído o error de red -> degradación
            return [], f"{etiqueta} no disponible"
        # Descarta ofertas con datos inconsistentes en vez de propagar basura (EC-04).
        validas = [o for o in ofertas if o.monto_mensual.es_positivo()]
        return validas, None
