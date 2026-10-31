from fastapi import APIRouter

from app.services.self_evolution import SelfEvolutionEngine

router = APIRouter(prefix="/api/v1")

@router.get("/evolution")
async def evolution_state():
    engine = SelfEvolutionEngine()
    project_state = {
        "voice_to_text": True,
        "voice_identity": True,
        "auth": True,
        "dashboard": True,
        "ai_engine": True,
    }
    return engine.evaluate(project_state)
