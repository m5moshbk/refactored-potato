from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TranscriptResponse(BaseModel):
    filename: str
    transcript: str
    language: str = "ar"
    status: str = "ok"

class VoiceVerifyResponse(BaseModel):
    user_id: int
    matched: bool
    score: float
    status: str
