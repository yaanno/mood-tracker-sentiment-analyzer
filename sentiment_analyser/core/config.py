from enum import Enum
from typing import Optional, List
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
    
    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Environment the application is running in",
        env="ENVIRONMENT"
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
    MODEL_CACHE_DIR: DirectoryPath = Field(
        default=Path(".cache"),
        description="Directory to cache downloaded models"
    )
    ALLOWED_HOSTS_STR: str = Field(
        default="localhost,127.0.0.1",
        alias="ALLOWED_HOSTS",
        description="Comma-separated list of allowed hosts"
    )
    BACKEND_CORS_ORIGINS_STR: str = Field(
        default="http://localhost:8000,http://127.0.0.1:8000",
        alias="BACKEND_CORS_ORIGINS",
        description="Comma-separated list of origins allowed to make cross-origin requests"
    )

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Parse comma-separated hosts into a list."""
        return [host.strip() for host in self.ALLOWED_HOSTS_STR.split(",") if host.strip()]

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS_STR.split(",") if origin.strip()]
    RATE_LIMIT: str = Field(
        default="100/minute",
        description="Rate limit in the format of 'number/period' (e.g. '100/minute', '1000/hour')"
    )
    MODEL_NAME: str = Field(
        default="SamLowe/roberta-base-go_emotions",
        description="Name of the Hugging Face model to use for sentiment analysis"
    )
    SERVER_HOST: str = Field(
        default="0.0.0.0",
        description="Host to bind the server to"
    )
    SERVER_PORT: int = Field(
        default=8000,
        description="Port to run the server on",
        ge=1,
        le=65535
    )

    @field_validator("BACKEND_CORS_ORIGINS_STR")
    def validate_cors_origins(cls, v: str) -> str:
        """Validate that CORS origins are valid URLs."""
        for origin in v.split(","):
            origin = origin.strip()
            if origin and not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid origin URL '{origin}'. Must start with http:// or https://")
        return v

    @field_validator("ALLOWED_HOSTS_STR")
    def validate_allowed_hosts(cls, v: str) -> str:
        """Validate allowed hosts string."""
        if not v.strip():
            raise ValueError("ALLOWED_HOSTS cannot be empty")
        return v.strip('"')

    @field_validator("RATE_LIMIT")
    def validate_rate_limit(cls, v: str) -> str:
        """Validate rate limit format."""
        parts = v.split("/")
        if len(parts) != 2:
            raise ValueError("Rate limit must be in format 'number/period'")
        try:
            int(parts[0])
        except ValueError:
            raise ValueError("Rate limit number must be an integer")
        if parts[1] not in ["second", "minute", "hour", "day"]:
            raise ValueError("Rate limit period must be one of: second, minute, hour, day")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
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
