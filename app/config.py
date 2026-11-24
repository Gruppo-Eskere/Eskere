import secrets
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BenzinaChiara"
    database_url: str = "sqlite:///./benzina_chiara.db"
    secret_key: str | None = None
    external_api_base_url: str = "https://api.open-meteo.com/v1"
    import_province_filter: str = ""
    import_max_rows: int = 0
    cookie_secure: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.secret_key:
        settings.secret_key = secrets.token_urlsafe(32)
    return settings
