"""Configuración por variables de entorno (nunca credenciales en código)."""
from __future__ import annotations

from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COTIZACION_", env_file=".env")

    tasa_impuesto: Decimal = Decimal("0.12")
    vigencia_minutos: int = 60
    timeout_socios: float = 2.0
    modo_banco: str = "ok"
    modo_aseguradora: str = "ok"
    # Si se define una URL, se usa el adaptador HTTP real; si queda vacía, el mock.
    # Mismo puerto, distinto adaptador.
    catalogo_url: str | None = None
    banco_url: str | None = None
    aseguradora_url: str | None = None


def get_settings() -> Settings:
    return Settings()
