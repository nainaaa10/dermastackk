"""
Application Configuration Settings.
Loads and validates environment variables using Pydantic Settings.
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # General Environment
    APP_NAME: str = "Dermastack API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEMO_MODE: bool = True

    # Server Binding
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Cross-Origin Resource Sharing (CORS)
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Database Configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dermastack"
    MONGODB_TIMEOUT_MS: int = 2000  # Fast timeout so startup isn't blocked if Mongo is offline

    # Machine Learning Settings
    MODEL_WEIGHTS_PATH: str = "ml/weights/best_hybrid_skin_model.pt"
    MODEL_VERSION: str = "v1.0.0-experimental"
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB

    # Security & Privacy
    ALLOW_IMAGE_PERSISTENCE: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
