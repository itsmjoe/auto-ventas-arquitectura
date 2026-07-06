"""Configuración del servicio de Reserva."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RESERVA_", env_file=".env")

    # URL del microservicio de Cotización. Si no se define, se usa un mock vacío.
    cotizacion_url: str | None = None
    timeout: float = 2.0


def get_settings() -> Settings:
    return Settings()
