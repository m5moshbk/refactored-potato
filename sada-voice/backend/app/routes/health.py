from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.db import engine

router = APIRouter(tags=["operations"])


@router.get("/health")
def health():
    """Liveness probe: confirms that the API process can answer requests."""
    return {
        "status": "ok",
        "service": "m5mosh-voice-nexus",
        "environment": settings.environment,
        "capabilities": {
            "browser_speech_to_text": True,
            "server_speech_to_text": False,
            "voice_biometrics": False,
            "organization_dashboard": False,
        },
        "security": {
            "voice_biometrics_enabled": settings.voice_identity_enabled,
            "raw_audio_persistence": False,
        },
    }


@router.get("/ready")
def readiness():
    """Readiness probe: confirms the configured database accepts a simple query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Configured database is unavailable.")
    return {"status": "ready", "database": "reachable"}
