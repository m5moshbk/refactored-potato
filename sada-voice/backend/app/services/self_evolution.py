from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    key: str
    label: str
    weight: int
    enabled: bool
    evidence: str
    next_step: str


class SelfEvolutionEngine:
    """Deterministic readiness evaluator; it never changes code or system state."""

    def evaluate(self, capabilities: list[Capability]) -> dict:
        total = sum(item.weight for item in capabilities)
        earned = sum(item.weight for item in capabilities if item.enabled)
        score = round((earned / total) * 100) if total else 0
        available = [item.key for item in capabilities if item.enabled]
        blocked = [
            {
                "capability": item.key,
                "label": item.label,
                "evidence": item.evidence,
                "next_step": item.next_step,
            }
            for item in capabilities
            if not item.enabled
        ]

        return {
            "score": score,
            "status": "prototype" if score < 70 else "pre_production_review",
            "production_ready": False,
            "evaluation_type": "deterministic_configuration_review",
            "autonomous_changes": False,
            "available_capabilities": available,
            "gaps": blocked,
            "next_actions": [item["next_step"] for item in blocked],
            "summary": (
                "هذا تقييم إرشادي مبني على الإعدادات والقدرات المعلنة؛ "
                "لا ينفذ تغييرات تلقائية ولا يثبت جودة النماذج أو الامتثال."
            ),
            "motto": "Voice • Identity • Access • Future",
        }
