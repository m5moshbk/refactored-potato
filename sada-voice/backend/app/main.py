from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routes.audio import router as audio_router
from app.routes.auth import router as auth_router
from app.routes.evolution import router as evolution_router
from app.routes.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables and not settings.is_production:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description=(
        "Arabic-first voice accessibility foundation. Voice biometrics remain "
        "disabled until a consent-based, independently evaluated model is integrated."
    ),
    docs_url="/docs" if settings.debug or not settings.is_production else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(audio_router)
app.include_router(evolution_router)
