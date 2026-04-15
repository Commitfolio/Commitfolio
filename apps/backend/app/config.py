from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    github_client_id: str = os.getenv("GITHUB_CLIENT_ID", "")
    github_client_secret: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    github_callback_url: str = os.getenv(
        "GITHUB_CALLBACK_URL",
        "http://localhost:8000/api/v1/auth/github/callback",
    )
    github_scope: str = os.getenv("GITHUB_SCOPE", "read:user")
    frontend_app_url: str = os.getenv("FRONTEND_APP_URL", "http://localhost:5173")
    session_secret: str = os.getenv("SESSION_SECRET", "dev-session-secret-change-me")
    cors_origin: str = os.getenv("BACKEND_CORS_ORIGIN", "http://localhost:5173")


@lru_cache
def get_settings() -> Settings:
    return Settings()
