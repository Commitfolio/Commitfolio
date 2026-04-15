from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.dependencies import get_github_service
from app.api.routes import analysis_events, analysis_jobs, auth, repositories
from app.config import Settings, get_settings
from app.db import create_db_engine, create_session_factory, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db(app.state.db_engine)
    yield


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(title="Commitfolio API", version="0.1.0", lifespan=lifespan)
    app.state.settings = resolved_settings
    app.state.github_access_tokens = {}
    app.state.db_engine = create_db_engine(resolved_settings.database_url)
    app.state.db_session_factory = create_session_factory(app.state.db_engine)

    app.add_middleware(
        SessionMiddleware,
        secret_key=resolved_settings.session_secret,
        same_site="lax",
        https_only=False,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved_settings.cors_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(repositories.router)
    app.include_router(analysis_jobs.router)
    app.include_router(analysis_events.router)

    return app


app = create_app()
