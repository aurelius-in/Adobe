from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    FIREFLY_API_KEY: str | None = None
    FIREFLY_WORKSPACE_ID: str | None = None
    OPENAI_API_KEY: str | None = None
    LOG_LEVEL: str = "INFO"


