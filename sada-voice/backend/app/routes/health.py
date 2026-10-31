from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["operations"])


@router.get("/health")
def health():
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
