"""Adaptador outbound: repositorio de reservas en memoria."""
from __future__ import annotations

from reserva.domain.reserva import Reserva


class RepositorioMemoria:
    def __init__(self) -> None:
        self._por_id: dict[str, Reserva] = {}

    def guardar(self, reserva: Reserva) -> None:
        self._por_id[reserva.id] = reserva

    def obtener(self, reserva_id: str) -> Reserva | None:
        return self._por_id.get(reserva_id)
