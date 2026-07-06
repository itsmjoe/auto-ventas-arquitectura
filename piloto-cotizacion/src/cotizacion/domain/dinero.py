"""Value Object Dinero: aritmética monetaria segura en USD.

Usa Decimal con redondeo bancario (ROUND_HALF_EVEN) para evitar errores de
centavos (EC-10). El monto nunca es negativo (EC-12): las restas se acotan a 0.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

CENTAVOS = Decimal("0.01")
MONEDA = "USD"


@dataclass(frozen=True)
class Dinero:
    monto: Decimal
    moneda: str = MONEDA

    def __post_init__(self) -> None:
        if self.moneda != MONEDA:
            raise ValueError(f"El piloto solo admite {MONEDA}, se recibió {self.moneda}")
        normalizado = self._normalizar(self.monto)
        if normalizado < 0:
            raise ValueError("Dinero no puede ser negativo")
        object.__setattr__(self, "monto", normalizado)

    @staticmethod
    def _normalizar(valor: Decimal | int | str) -> Decimal:
        return Decimal(str(valor)).quantize(CENTAVOS, rounding=ROUND_HALF_EVEN)

    @classmethod
    def de(cls, valor: Decimal | int | str | float) -> Dinero:
        return cls(Decimal(str(valor)))

    @classmethod
    def cero(cls) -> Dinero:
        return cls(Decimal("0"))

    def sumar(self, otro: Dinero) -> Dinero:
        return Dinero(self.monto + otro.monto)

    def restar(self, otro: Dinero) -> Dinero:
        """Resta acotada a cero: un descuento nunca deja el total negativo (EC-12)."""
        resultado = self.monto - otro.monto
        return Dinero(resultado if resultado > 0 else Decimal("0"))

    def multiplicar(self, factor: Decimal | int | str | float) -> Dinero:
        return Dinero(self.monto * Decimal(str(factor)))

    def es_positivo(self) -> bool:
        return self.monto > 0
