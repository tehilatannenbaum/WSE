import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./travel_assistant.db"
    JWT_SECRET: str = "replace-with-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()

if settings.JWT_SECRET == "replace-with-a-long-random-secret":
    logger.warning(
        "WARNING: Using default/insecure JWT_SECRET placeholder! "
        "For production environments, please set a strong random JWT_SECRET in your .env file."
    )

