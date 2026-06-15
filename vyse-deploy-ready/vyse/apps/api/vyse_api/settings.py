from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "VYSE API"
    environment: str = "dev"
    # When true, the API creates the pgvector extension + tables on boot. Safe/idempotent;
    # the single API service should own this (keep it false on the worker).
    auto_init_db: bool = True

    # Postgres (pgvector image). asyncpg driver.
    database_url: str = "postgresql+asyncpg://vyse:vyse@localhost:5432/vyse"
    redis_url: str = "redis://localhost:6379"

    # Auth: "dev" injects a seeded workspace so the app runs with zero external keys.
    #       "clerk" verifies real Clerk JWTs.
    auth_mode: str = "dev"
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""
    clerk_webhook_secret: str = ""

    # AI: if openai_api_key is empty, a deterministic stub provider is used so the
    # full pipeline still runs offline.
    openai_api_key: str = ""
    ai_chat_model: str = "gpt-4o-mini"
    ai_vision_model: str = "gpt-4o-mini"
    ai_embed_model: str = "text-embedding-3-small"
    embed_dim: int = 1536

    # Data sources
    youtube_api_key: str = ""  # optional; oEmbed works without it for previews

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro: str = ""
    stripe_price_agency: str = ""

    # Limits
    rate_limit_per_min: int = 120
    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
