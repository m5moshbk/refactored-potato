from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import field_validator, model_validator
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
    debug: bool = False

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgres://"):
            return "postgresql://" + value[len("postgres://"):]
        return value

    @model_validator(mode="after")
    def validate_production_configuration(self):
        if self.environment.lower() == "production":
            if len(self.secret_key) < 32:
                raise ValueError("Production requires a random SECRET_KEY of at least 32 characters.")
            if not self.database_url.startswith(("postgresql://", "postgresql+psycopg2://")):
                raise ValueError("Production requires a persistent PostgreSQL DATABASE_URL.")
            origins = self.allowed_origins
            if not origins or "*" in origins:
                raise ValueError("Production CORS_ORIGINS must contain exact allowed origins; wildcards are forbidden.")
            for origin in origins:
                try:
                    parsed = urlsplit(origin)
                    _ = parsed.port
                except ValueError as exc:
                    raise ValueError("Each production CORS origin must be a valid origin URL.") from exc
                if (
                    parsed.scheme != "https"
                    or not parsed.hostname
                    or parsed.username
                    or parsed.password
                    or parsed.path
                    or parsed.query
                    or parsed.fragment
                ):
                    raise ValueError("Production CORS origins must be HTTPS origins without paths, credentials, queries, or fragments.")
                hostname = parsed.hostname.lower()
                if hostname == "localhost" or hostname.endswith(".localhost") or hostname in {"127.0.0.1", "::1"}:
                    raise ValueError("Production CORS_ORIGINS cannot contain localhost origins.")
            if self.debug:
                raise ValueError("DEBUG must be disabled in production.")
            if self.auto_create_tables:
                raise ValueError("AUTO_CREATE_TABLES must be disabled in production.")
        if self.access_token_minutes < 5 or self.access_token_minutes > 120:
            raise ValueError("ACCESS_TOKEN_MINUTES must be between 5 and 120.")
        if self.max_audio_bytes < 1024 or self.max_audio_bytes > 25 * 1024 * 1024:
            raise ValueError("MAX_AUDIO_BYTES must be between 1 KB and 25 MB.")
        return self

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
