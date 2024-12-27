from enum import Enum
from typing import Optional
from pathlib import Path

from pydantic import Field, DirectoryPath, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class BaseAppSettings(BaseSettings):
    """Base settings class with shared configuration."""
    
    ENV: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Environment the application is running in"
    )
    DEBUG: bool = Field(
        default=False,
        description="Debug mode flag"
    )
    PROJECT_NAME: str = Field(
        default="Sentiment Analyzer",
        description="Project name"
    )
    VERSION: str = Field(
        default="0.1.0",
        description="Project version"
    )
    API_PREFIX: str = Field(
        default="/api/v1",
        description="API prefix for all endpoints"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

class APISettings(BaseAppSettings):
    """API specific settings."""
    
    HOST: str = Field(
        default="0.0.0.0",
        description="Host to bind the API server"
    )
    PORT: int = Field(
        default=8000,
        description="Port to bind the API server"
    )
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )

class MLModelSettings(BaseAppSettings):
    """Machine Learning model settings."""
    
    MODEL_NAME: str = Field(
        default="SamLowe/roberta-base-go_emotions",
        description="Name of the pretrained model to use"
    )
    MODEL_CACHE_DIR: Optional[DirectoryPath] = Field(
        default=None,
        description="Directory to cache downloaded models"
    )
    BATCH_SIZE: int = Field(
        default=32,
        description="Batch size for model inference"
    )
    MAX_SEQUENCE_LENGTH: int = Field(
        default=512,
        description="Maximum sequence length for tokenization"
    )

    @field_validator("MODEL_CACHE_DIR")
    def validate_cache_dir(cls, v: Optional[Path]) -> Optional[Path]:
        if v is not None:
            v.mkdir(parents=True, exist_ok=True)
        return v

class RateLimitSettings(BaseAppSettings):
    """Rate limiting settings."""
    
    ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    REQUESTS_LIMIT: int = Field(
        default=100,
        description="Maximum number of requests"
    )
    WINDOW_SIZE: int = Field(
        default=3600,
        description="Time window in seconds"
    )

class LoggingSettings(BaseAppSettings):
    """Logging configuration settings."""
    
    LEVEL: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )
    FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    FILE_PATH: Optional[Path] = Field(
        default=None,
        description="Log file path"
    )

class Settings(BaseAppSettings):
    """Main settings class that combines all settings."""
    
    app: BaseAppSettings = BaseAppSettings()
    api: APISettings = APISettings()
    model: MLModelSettings = MLModelSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    logging: LoggingSettings = LoggingSettings()


_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Get singleton instance of Settings.
    
    Returns:
        Settings: The application settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
