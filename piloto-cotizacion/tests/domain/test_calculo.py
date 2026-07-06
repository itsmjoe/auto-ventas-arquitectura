from decimal import Decimal

import pytest

from cotizacion.domain import calculo
from cotizacion.domain.calculo import TasaImpuestoInvalida
from cotizacion.domain.dinero import Dinero


def test_calcular_impuestos():
    impuestos = calculo.calcular_impuestos(Dinero.de("1000.00"), Decimal("0.12"))
    assert impuestos.monto == Decimal("120.00")


def test_calcular_total_suma_precio_e_impuestos():
    total = calculo.calcular_total(Dinero.de("1000.00"), Dinero.de("120.00"))
    assert total.monto == Decimal("1120.00")


def test_calcular_total_aplica_descuento_acotado():
    total = calculo.calcular_total(
        Dinero.de("1000.00"), Dinero.de("120.00"), descuentos=Dinero.de("2000.00")
    )
    assert total.monto == Decimal("0.00")


def test_tasa_ausente_es_error_explicito():
    with pytest.raises(TasaImpuestoInvalida):
        calculo.calcular_impuestos(Dinero.de("1000.00"), None)


def test_tasa_fuera_de_rango_es_error():
    with pytest.raises(TasaImpuestoInvalida):
        calculo.validar_tasa(Decimal("1.5"))
