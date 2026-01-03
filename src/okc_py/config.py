"""Configuration settings for OKC API wrapper."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """OKC API configuration settings."""

    # OKC API Configuration
    BASE_URL: str = "https://okc.ertelecom.ru/yii"

    # Request Configuration
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    REQUESTS_PER_SECOND: float = 5.0

    # Logging (loguru format)
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )
