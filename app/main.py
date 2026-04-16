from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

try:
    from app.api.routes_auth import router as auth_router
except ImportError:
    auth_router = None

try:
    from app.api.routes_chat import router as chat_router
except ImportError:
    chat_router = None

try:
    from app.db.base import Base
except ImportError:
    Base = None

try:
    from app.db.session import engine
except ImportError:
    engine = None


def is_cors_enabled() -> bool:
    """Return whether CORS middleware should be enabled."""
    return settings.cors_enabled


def get_cors_origins() -> list[str]:
    """Return the list of allowed CORS origins from the environment."""
    raw_origins = settings.cors_allow_origins
    if not raw_origins.strip():
        return ["*"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def setup_cors(app: FastAPI) -> None:
    """Attach CORS middleware to the application when enabled."""
    if not is_cors_enabled():
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def include_routers(app: FastAPI) -> None:
    """Register API routers that are available in the project."""
    if auth_router is not None:
        app.include_router(auth_router)

    if chat_router is not None:
        app.include_router(chat_router)


async def create_tables() -> None:
    """Create database tables on application startup."""
    if Base is None or engine is None:
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Run startup tasks before the application begins serving requests."""
    await create_tables()
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    setup_cors(app)
    include_routers(app)

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {
            "status": "ok",
            "environment": settings.env,
        }

    return app


app = create_app()
