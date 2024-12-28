"""Environment-specific settings management."""
from typing import Optional, List
from pathlib import Path

from pydantic import Field, DirectoryPath, field_validator
from pydantic_settings import BaseSettings

from .config import Environment, LogLevel, BaseAppSettings

class BaseApplicationSettings(BaseAppSettings):
    """Base application settings."""
    
    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Environment the application is running in",
        env="ENVIRONMENT"
    )
    DEBUG: bool = Field(
        default=False,
        description="Debug mode flag",
        env="DEBUG"
    )
    PROJECT_NAME: str = Field(
        default="Sentiment Analyzer",
        description="Project name",
        env="PROJECT_NAME"
    )
    VERSION: str = Field(
        default="0.1.0",
        description="Project version",
        pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$"
    )
    API_PREFIX: str = Field(
        default="/api/v1",
        description="API prefix for all endpoints",
        pattern="^/[a-zA-Z0-9/_-]+$"
    )
    MODEL_CACHE_DIR: DirectoryPath = Field(
        default=Path(".cache"),
        description="Directory to cache downloaded models",
        env="MODEL_CACHE_DIR"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="List of allowed hosts",
        env="ALLOWED_HOSTS"
    )
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ],
        description="List of origins allowed to make cross-origin requests",
        env="CORS_ORIGINS"
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
    CORS_ORIGINS: List[str] = Field(
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
    BATCH_SIZE: int = Field(
        default=32,
        description="Batch size for model inference"
    )
    MAX_SEQUENCE_LENGTH: int = Field(
        default=512,
        description="Maximum sequence length for tokenization"
    )

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


class SecuritySettings(BaseSettings):
    """Security-related settings."""
    
    SECRET_KEY: str = Field(
        default="super-secret-key-please-change-in-production",
        description="Secret key for tokens and cryptography",
        env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration in minutes",
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    ENCRYPTION_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm for JWT token encryption",
        env="ENCRYPTION_ALGORITHM"
    )



class Settings(BaseAppSettings):
    """Main settings class that combines all settings."""

    app: BaseApplicationSettings = BaseApplicationSettings()
    api: APISettings = APISettings()
    security: SecuritySettings = SecuritySettings()
    model: MLModelSettings = MLModelSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    logging: LoggingSettings = LoggingSettings()

    @field_validator("app")
    def validate_app_settings(cls, v: BaseApplicationSettings) -> BaseApplicationSettings:
        """Validate application settings based on environment."""
        if v.ENVIRONMENT == Environment.PRODUCTION:
            assert v.DEBUG is False, "Debug mode must be disabled in production"
            assert "localhost" not in v.ALLOWED_HOSTS, "Localhost not allowed in production"
            assert len(v.ALLOWED_HOSTS) > 0, "No allowed hosts configured"
        return v

# Singleton instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
        """Get singleton instance of settings."""
        global _settings
        if _settings is None:
            _settings = Settings()
        return _settings