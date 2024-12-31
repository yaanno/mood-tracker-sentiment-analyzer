"""Base configuration and enums."""

import os
from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def get_env_file() -> str:
    """Get the appropriate .env file based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    base_path = Path(__file__).parent.parent.parent
    env_file = base_path / f".env.{env}"
    default_env = base_path / ".env"
    return str(env_file if env_file.exists() else default_env)


class BaseAppSettings(BaseSettings):
    """Base settings class with shared configuration."""

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_default=True,
        extra="ignore",
    )
