import json
from pathlib import Path
from backend.agents import reason_about_adherence, generate_weekly_insight
from backend.guardrails import check_emergency, emergency_response, scope_check

# Points to the project root, then into knowledge_base/
# __file__ = orchestrator.py → .parent = backend/ → .parent = project root
KB_PATH = Path(__file__).parent.parent / "knowledge_base"


def _load(name):
    with open(KB_PATH / name) as f:
        return json.load(f)


def process_message(user, message):
    """Main orchestration entry point."""
    # 1. GUARDRAIL: emergency override
    if check_emergency(message):
        return emergency_response(user["name"], user["caregiver"])

    # 2. Load knowledge base context
    drugs = _load("drug_profiles.json")
    side_effects = _load("side_effects.json")
    tones = _load("tone_profiles.json")

    drug_ctx = {d: drugs.get(d, {}) for d in user["medications"]}
    side_ctx = {d: side_effects.get(d, {}) for d in user["medications"]}
    tone = tones.get(user["persona"], {}).get("tone", "warm and clear")

    # 3. REASON
    result = reason_about_adherence(user, message, drug_ctx, side_ctx, tone)

    # 4. Scope guardrail post-check
    if scope_check(message):
        result["user_message"] = (
            "I can't advise changing your dose — that's a decision for your "
            "doctor or pharmacist. I'd be glad to help you prepare questions "
            "for them, though!"
        )
        result["intervention_tier"] = max(result.get("intervention_tier", 1), 2)

    # 5. Escalation payload for Tier 3/4
    if result.get("intervention_tier", 1) >= 3 and user["caregiver"]:
        result["escalation_payload"] = {
            "type": "caregiver_alert" if result["intervention_tier"] == 3 else "clinical_flag",
            "notify": user["caregiver"],
            "summary": result.get("reasoning", "")[:200],
        }

    return result


def weekly_report(user, data):
    return generate_weekly_insight(user, data)
