from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRES_SECONDS: int = Field(3600, ge=60, le=86400)
    JWT_ISSUER: str = 'lecture-pulse'
    DATABASE_URL: str = 'sqlite:///./lecture_pulse.db'
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    LOG_JSON: bool = True
    JOIN_CODE_LENGTH: int = Field(8, ge=6, le=12)
    APP_ENV: str = 'dev'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith('sqlite'):
            raise ValueError("DATABASE_URL must start with 'sqlite'")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
