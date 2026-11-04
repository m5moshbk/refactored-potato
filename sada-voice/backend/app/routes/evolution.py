from fastapi import APIRouter

from app.config import settings
from app.services.self_evolution import Capability, SelfEvolutionEngine

router = APIRouter(prefix="/api/v1", tags=["readiness"])


@router.get("/evolution")
def evolution_state():
    capabilities = [
        Capability(
            "api",
            "واجهة API",
            15,
            True,
            "FastAPI application is defined in app/main.py.",
            "Keep API contracts versioned and add automated integration coverage.",
        ),
        Capability(
            "authentication",
            "مصادقة الحسابات",
            15,
            len(settings.secret_key) >= 32,
            "A random signing key of at least 32 characters is required.",
            "Configure a unique random SECRET_KEY in the deployment environment.",
        ),
        Capability(
            "database",
            "قاعدة البيانات",
            10,
            bool(settings.database_url),
            "DATABASE_URL is present; connectivity and migrations are not verified here.",
            "Add reviewed migrations, backups, and a live connectivity check.",
        ),
        Capability(
            "browser_speech",
            "تحويل الكلام إلى نص عبر المتصفح",
            10,
            True,
            "The frontend uses browser speech-recognition support when available.",
            "Test Arabic recognition across supported browsers and disclose browser-provider privacy behavior.",
        ),
        Capability(
            "server_speech",
            "تحويل الكلام إلى نص على الخادم",
            15,
            False,
            "No server-side speech provider or self-hosted model is configured.",
            "Select and evaluate a provider or self-hosted model with an approved privacy and cost profile.",
        ),
        Capability(
            "voice_biometrics",
            "التحقق البيومتري من الصوت",
            15,
            False,
            "No validated speaker-embedding or anti-spoof model is integrated.",
            "Complete consent, liveness/anti-spoof evaluation, FAR/FRR testing, encryption, and deletion controls before enabling biometrics.",
        ),
        Capability(
            "organization_dashboard",
            "لوحة المؤسسات",
            10,
            False,
            "No organization tenancy, roles, or dashboard backend is implemented.",
            "Design tenant isolation, role-based access, and an auditable organization dashboard.",
        ),
        Capability(
            "production_assurance",
            "ضمان الجاهزية الإنتاجية",
            10,
            False,
            "No current end-to-end, security, accessibility, or deployment verification is recorded.",
            "Run and record CI, security review, accessibility checks, and staging acceptance tests.",
        ),
    ]
    return SelfEvolutionEngine().evaluate(capabilities)
