from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(default=None, max_length=120)
    password: str = Field(min_length=12, max_length=64)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=64)


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

    @field_validator("score")
    @classmethod
    def validate_score(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("score must be between 0 and 1")
        return value
