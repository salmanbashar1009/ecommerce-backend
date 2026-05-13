from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database and Redis
    DATABASE_URL: str = "postgresql+asyncpg://postgres:1009@localhost:5432/ecommerce"
    REDIS_URL: str = "redis://localhost:6379"

    # API Prefix
    API_V1_PREFIX: str = "/api/v1"

    # Stripe
    STRIPE_API_KEY: str 

     # Rate Limiting (for SlowAPI)
    RATE_LIMIT_DEFAULT: str = "100/minute"

    # Define the .env fields here so Pydantic knows to look for them
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    STRIPE_API_KEY: str


     # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Pydantic V2 uses model_config (not "class config")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # This prevents errors if there are extra variables in .env
    )

settings = Settings()