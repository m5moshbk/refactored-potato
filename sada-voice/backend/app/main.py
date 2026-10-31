from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routes.audio import router as audio_router
from app.routes.auth import router as auth_router
from app.routes.health import router as health_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sada Voice API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(audio_router)

@app.get("/")
async def root():
    return {"message": "Sada Voice API running"}
