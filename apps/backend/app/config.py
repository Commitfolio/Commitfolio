from dataclasses import dataclass
from functools import lru_cache
import os


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default

    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    github_client_id: str = os.getenv("GITHUB_CLIENT_ID", "")
    github_client_secret: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    github_callback_url: str = os.getenv(
        "GITHUB_CALLBACK_URL",
        "http://localhost:8000/api/v1/auth/github/callback",
    )
    github_scope: str = os.getenv("GITHUB_SCOPE", "read:user repo read:org")
    frontend_app_url: str = os.getenv("FRONTEND_APP_URL", "http://localhost:5173")
    session_secret: str = os.getenv("SESSION_SECRET", "dev-session-secret-change-me")
    session_cookie_same_site: str = os.getenv("SESSION_COOKIE_SAME_SITE", "lax")
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in {"1", "true", "yes", "on"}
    cors_origin: str = os.getenv("BACKEND_CORS_ORIGIN", "http://localhost:5173")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./commitfolio.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_timeout_seconds: float = _get_float_env("OPENAI_TIMEOUT_SECONDS", 8.0)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
