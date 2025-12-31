from pydantic import (
    Field,
)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_URL: str = Field()
    USERNAME: str = Field()
    PASSWORD: str = Field()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
