from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "M5mOsH Voice Nexus API"
    environment: str = "development"
    database_url: str = "sqlite:///./sada_voice.db"
    secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    cors_origins: str = "http://localhost:3000"
    max_audio_bytes: int = 15 * 1024 * 1024
    auto_create_tables: bool = False
    speech_provider: str = "browser"
    voice_identity_enabled: bool = False
    debug: bool = False

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
