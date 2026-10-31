from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.models import User
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["audio"])

ALLOWED_AUDIO_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/webm",
    "audio/ogg",
    "audio/aac",
}


async def _validate_upload(file: UploadFile) -> bytes:
    content_type = (file.content_type or "").lower().split(";")[0].strip()
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio format.")

    content = await file.read(settings.max_audio_bytes + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The audio file is empty.")
    if len(content) > settings.max_audio_bytes:
        raise HTTPException(status_code=413, detail="Audio file exceeds the configured size limit.")
    return content


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    await _validate_upload(file)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Server transcription is not configured. Use the browser speech feature "
            "or connect an approved speech provider before enabling this endpoint."
        ),
    )


@router.post("/voiceprint", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_voiceprint(
    _: UploadFile = File(...),
    __: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Voice identity enrollment is disabled until a consent-based biometric model is integrated and evaluated.",
    )


@router.post("/verify", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def verify_voice(
    _: UploadFile = File(...),
    __: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Voice identity verification is not available. No audio hash is used as a biometric identity.",
    )
