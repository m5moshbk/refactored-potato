from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import User
from app.schemas import UserCreate, UserLogin, TokenResponse

router = APIRouter(prefix="/api/v1")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token(email: str):
    expire = datetime.utcnow() + timedelta(hours=12)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

@router.post("/signup", response_model=TokenResponse)
async def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=pwd_context.hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.email)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_token(user.email)
    return {"access_token": token, "token_type": "bearer"}
