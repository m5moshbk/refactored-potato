from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Sada Voice"
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/sada_voice"
    SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = ""
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
