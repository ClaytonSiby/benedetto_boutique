from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Union
from functools import lru_cache


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "B Boutique API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # CORS Settings
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000", "http://localhost:8000"]

    @property
    def get_cors_origins(self) -> List[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

    # Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "b_boutique"
    # SSL mode for managed Postgres providers. Not needed for local Postgres.
    POSTGRES_SSLMODE: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        base = f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if self.POSTGRES_SSLMODE:
            return f"{base}?sslmode={self.POSTGRES_SSLMODE}"
        return base

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Celery Settings
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @property
    def CELERY_BROKER(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def CELERY_BACKEND(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    # Session Settings
    SESSION_SECRET_KEY: str
    SESSION_COOKIE_NAME: str = "b_boutique_session"
    SESSION_MAX_AGE: int = 86400  # 24 hours

    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SendGrid Email Settings
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@bboutique.com"
    ADMIN_EMAIL: str = "admin@bboutique.com"

    # Stripe Payment Settings
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_CURRENCY: str = "ZAR"

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:3000"

    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    USE_CLOUDINARY: bool = False  # Toggle between local and Cloudinary storage

    # API Documentation
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"

    model_config = SettingsConfigDict(
        # Load from environment by default; fall back to .env if present
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
