from decimal import Decimal

import pytest

from cotizacion.domain.dinero import Dinero


def test_normaliza_a_dos_decimales_con_redondeo_bancario():
    # 2.675 -> 2.68 con ROUND_HALF_EVEN sobre la representación decimal exacta
    assert Dinero.de("2.675").monto == Decimal("2.68")
    # 2.665 -> 2.66 (redondeo al par)
    assert Dinero.de("2.665").monto == Decimal("2.66")


def test_suma_y_multiplicacion():
    assert Dinero.de("100.00").sumar(Dinero.de("50.50")).monto == Decimal("150.50")
    assert Dinero.de("100.00").multiplicar("0.12").monto == Decimal("12.00")


def test_resta_se_acota_a_cero():
    # Un descuento mayor que el monto no produce negativo (EC-12)
    assert Dinero.de("100.00").restar(Dinero.de("150.00")).monto == Decimal("0.00")


def test_no_admite_moneda_distinta_de_usd():
    with pytest.raises(ValueError):
        Dinero(Decimal("10"), moneda="EUR")


def test_no_admite_monto_negativo():
    with pytest.raises(ValueError):
        Dinero(Decimal("-1"))
