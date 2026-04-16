from __future__ import annotations

import os
from contextlib import asynccontextmanager
from importlib import import_module
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def _get_app_title() -> str:
    return os.getenv("APP_NAME", "llm-p")


def _get_environment() -> str:
    return os.getenv("ENV", "local")


def _is_cors_enabled() -> bool:
    return os.getenv("CORS_ENABLED", "").lower() in {"1", "true", "yes", "on"}


def _get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
    if not raw_origins.strip():
        return ["*"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _include_router_if_available(app: FastAPI, module_path: str) -> None:
    try:
        module = import_module(module_path)
    except Exception:
        return

    router = getattr(module, "router", None)
    if router is not None:
        app.include_router(router)


async def _run_create_all_if_possible() -> None:
    try:
        db_base = import_module("app.db.base")
        db_session = import_module("app.db.session")
    except Exception:
        return

    base = getattr(db_base, "Base", None)
    engine = getattr(db_session, "engine", None)
    metadata = getattr(base, "metadata", None)

    if metadata is None or engine is None:
        return

    if hasattr(engine, "sync_engine"):
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        return

    with engine.begin() as conn:
        metadata.create_all(bind=conn)


@asynccontextmanager
async def _lifespan(_: FastAPI):
    await _run_create_all_if_possible()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=_get_app_title(), lifespan=_lifespan)

    if _is_cors_enabled():
        app.add_middleware(
            CORSMiddleware,
            allow_origins=_get_cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    _include_router_if_available(app, "app.api.routes_auth")
    _include_router_if_available(app, "app.api.routes_chat")

    @app.get("/health")
    async def healthcheck() -> dict[str, Any]:
        return {
            "status": "ok",
            "environment": _get_environment(),
        }

    return app


app = create_app()
