from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.db.session import init_db, close_db
from app.core.cache import init_cache, close_cache

logger = setup_logging()

TAGS_METADATA = [
    {
        "name": "todos",
        "description": "CRUD-операции над задачами пользователя.",
    },
    {
        "name": "users",
        "description": "Управление пользователями.",
    },
    {
        "name": "healthcheck",
        "description": "Проверка работоспособности сервиса.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    await init_db()
    await init_cache()
    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    await close_cache()
    logger.info("Application shutdown complete")


# Swagger/ReDoc доступны только при DEBUG=True
_docs_url: Optional[str] = f"{settings.API_V1_STR}/docs" if settings.DEBUG else None
_redoc_url: Optional[str] = f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None
_openapi_url: Optional[str] = f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "## Todo Core Service\n\n"
        "Сервис управления задачами. \n\n"
        "### Авторизация\n"
    ),
    openapi_tags=TAGS_METADATA,
    openapi_url=_openapi_url,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["healthcheck"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }
