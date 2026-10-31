from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.db import SessionLocal
from app.models import VoiceProfile
from app.services.speech_to_text import SpeechToTextService
from app.services.voiceprint import VoicePrintService

router = APIRouter(prefix="/api/v1")

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    content = await file.read()
    service = SpeechToTextService()
    result = await service.transcribe_audio(content, file.filename)
    return result

@router.post("/voiceprint")
async def create_voiceprint(file: UploadFile = File(...), user_id: str = Form(...)):
    content = await file.read()
    fingerprint = VoicePrintService().create_fingerprint(content)

    db = SessionLocal()
    record = VoiceProfile(user_id=int(user_id), fingerprint=fingerprint)
    db.add(record)
    db.commit()
    db.close()

    return {
        "user_id": user_id,
        "voiceprint_status": "stored",
        "fingerprint": fingerprint,
    }

@router.post("/verify")
async def verify_voice(file: UploadFile = File(...), user_id: str = Form(...)):
    content = await file.read()
    candidate_hash = VoicePrintService().create_fingerprint(content)

    db = SessionLocal()
    profile = db.query(VoiceProfile).filter(VoiceProfile.user_id == int(user_id)).first()
    db.close()

    if not profile:
        return JSONResponse(status_code=404, content={"detail": "voice profile not found"})

    score = VoicePrintService().compare(profile.fingerprint, candidate_hash)

    return {
        "user_id": user_id,
        "matched": score >= 0.9,
        "score": score,
        "status": "verified" if score >= 0.9 else "mismatch",
    }
