from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    fingerprint = Column(String, nullable=False)
    model_version = Column(String, default="v1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AudioRecord(Base):
    __tablename__ = "audio_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    file_name = Column(String, nullable=False)
    transcript = Column(Text, nullable=True)
    language = Column(String, default="ar")
    confidence = Column(Float, default=0.0)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
