import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))
    )

    # CORS - comma-separated list of allowed origins, or "*" for all
    CORS_ORIGINS: str | list[str] = os.getenv("CORS_ORIGINS", "*")

    @classmethod
    def get_cors_origins(cls) -> str | list[str]:
        """Parse CORS_ORIGINS into a list if comma-separated, or return as-is."""
        origins = cls.CORS_ORIGINS
        if origins == "*":
            return "*"
        if "," in origins:
            return [o.strip() for o in origins.split(",")]
        return origins
