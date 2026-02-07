"""Environment configuration management using Pydantic Settings."""
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-based configuration."""

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Environment
    ENVIRONMENT: str = "local"  # local or production

    # Application Settings
    APP_NAME: str = "Service Marketplace API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8002

    # Database Settings
    DATABASE_URL: str
    DB_ECHO: bool = True
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Settings
    REDIS_URL: str
    REDIS_OTP_DB: int = 1

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OTP Settings
    OTP_LENGTH: int = 6
    OTP_EXPIRY_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3

    # Email Settings (SMTP)
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Service Marketplace"

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8081"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB in bytes
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_local(self) -> bool:
        """Check if running in local environment."""
        return self.ENVIRONMENT.lower() == "local"

    def __init__(self, **kwargs):
        """Initialize settings with environment-specific overrides."""
        super().__init__(**kwargs)

        # Production-specific settings
        if self.is_production:
            self.DEBUG = False
            self.DB_ECHO = False
            # Production has standard token expiry
            # Ensure CORS is properly configured
            if not self.CORS_ORIGINS or self.CORS_ORIGINS == ["http://localhost:3000"]:
                # In production, CORS_ORIGINS should be set explicitly
                pass

        # Local-specific settings
        if self.is_local:
            self.DEBUG = True
            self.DB_ECHO = True
            # Local can have shorter token expiry for testing if needed
            # CORS allows localhost origins by default


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()

