EMERGENCY_KEYWORDS = [
    "chest pain", "chest tight", "can't breathe", "cant breathe",
    "difficulty breathing", "swelling of face", "swollen lips",
    "allergic", "passed out", "unconscious", "severe bleeding",
    "dark urine", "slurred speech", "numbness", "dizzy and",
]

BLOCKED_REQUESTS = [
    "double my dose", "stop taking", "should i quit",
    "increase my dose", "how much can i take",
]


def check_emergency(user_message: str) -> bool:
    """Detect emergency symptoms that override normal flow."""
    msg = user_message.lower()
    return any(kw in msg for kw in EMERGENCY_KEYWORDS)


def emergency_response(user_name: str, caregiver: str | None) -> dict:
    alert = f"I'm alerting {caregiver} right now. " if caregiver else ""
    return {
        "adherence_status": "emergency",
        "root_cause": "medical_emergency",
        "risk_score": 5,
        "intervention_tier": 4,
        "reasoning": "Emergency symptom detected — bypassing normal flow.",
        "user_message": (
            f"🚨 {user_name}, these symptoms can be serious. "
            f"Please call emergency services (911) now or get to an ER. {alert}"
            "Do not wait."
        ),
        "escalation_payload": {"type": "emergency", "notify": caregiver},
    }


def scope_check(user_message: str) -> bool:
    """Detect requests to change dosage (scope violation)."""
    msg = user_message.lower()
    return any(b in msg for b in BLOCKED_REQUESTS)
