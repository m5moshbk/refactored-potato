class SelfEvolutionEngine:
    def __init__(self):
        self.modes = {
            "audio": "voice recognition",
            "identity": "voice-based authentication",
            "access": "secure access flows",
            "insight": "analytics and automation",
            "growth": "product expansion"
        }

    def evaluate(self, project_state: dict):
        score = 0
        reasons = []

        if project_state.get("voice_to_text"):
            score += 20
        else:
            reasons.append("أضف تحويل الكلام إلى نص")

        if project_state.get("voice_identity"):
            score += 20
        else:
            reasons.append("أضف بصمة صوتية للتحقق")

        if project_state.get("auth"):
            score += 20
        else:
            reasons.append("أضف نظام تسجيل دخول وأكثر أمانًا")

        if project_state.get("dashboard"):
            score += 20
        else:
            reasons.append("أضف لوحة تحكم للمؤسسات")

        if project_state.get("ai_engine"):
            score += 20
        else:
            reasons.append("أضف محرك ذكي يقيّم المشروع ويقترح التطوير")

        status = "ready" if score >= 80 else "evolving"
        return {
            "score": score,
            "status": status,
            "phase": self._phase(score),
            "next_actions": self._next_actions(project_state),
            "reasons": reasons,
            "self_growth_summary": self._summary(project_state),
        }

    def _phase(self, score: int):
        if score >= 90:
            return "scale-ready"
        if score >= 75:
            return "growth-stage"
        if score >= 50:
            return "prototype-stage"
        return "idea-stage"

    def _next_actions(self, project_state: dict):
        actions = []
        if not project_state.get("voice_to_text"):
            actions.append("تنفيذ خدمة تحويل الصوت إلى نص")
        if not project_state.get("voice_identity"):
            actions.append("إضافة بصمة صوتية مع مقارنة الهوية")
        if not project_state.get("dashboard"):
            actions.append("إنشاء لوحة تحكم لمقاييس المشروع")
        if not project_state.get("ai_engine"):
            actions.append("إضافة محرك تحليل ذكي يستنتج أولويات التطوير")
        if not actions:
            actions.append("توسيع الخدمات إلى مؤسسات ومراكز تعليمية وصحية")
        return actions

    def _summary(self, project_state: dict):
        features = []
        if project_state.get("voice_to_text"):
            features.append("voice-to-text")
        if project_state.get("voice_identity"):
            features.append("voice-identity")
        if project_state.get("auth"):
            features.append("secure-auth")
        if project_state.get("dashboard"):
            features.append("dashboard")
        if project_state.get("ai_engine"):
            features.append("adaptive-ai")

        return {
            "core_features": features,
            "motto": "Voice • Identity • Access • Future",
            "message": "المشروع قادر على التطور الذاتي من خلال تقييم نفسه وتحديد أولويات التطوير التلقائي."
        }
