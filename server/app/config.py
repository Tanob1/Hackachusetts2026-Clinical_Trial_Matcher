"""Configuration settings loaded from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/trial_matcher"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/trial_matcher_test"

    # JWT
    JWT_SECRET_KEY: str = "change-this-to-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ClinicalTrials.gov
    CTGOV_API_BASE: str = "https://clinicaltrials.gov/api/v2"
    CTGOV_SYNC_CRON: str = "0 3 * * *"
    CTGOV_SYNC_BATCH_SIZE: int = 1000

    # App
    APP_NAME: str = "Clinical Trial Matcher"
    CORS_ORIGINS: str = "http://localhost:8081,http://localhost:19006,exp://localhost:8081"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
