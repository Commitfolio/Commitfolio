from __future__ import annotations

from collections.abc import Generator

from fastapi import Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base


def create_db_engine(database_url: str) -> Engine:
    engine_options: dict[str, object] = {"future": True}

    if database_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}

        if database_url.endswith(":memory:"):
            engine_options["poolclass"] = StaticPool

    return create_engine(database_url, **engine_options)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def get_db_session(request: Request) -> Generator[Session, None, None]:
    session_factory: sessionmaker[Session] = request.app.state.db_session_factory

    with session_factory() as session:
        yield session
