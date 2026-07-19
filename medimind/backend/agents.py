import json
from backend.llm_client import call_llm

SYSTEM_PROMPT = """# ROLE
You are MediMind's Adherence Reasoning Agent — a clinical-grade AI
that reasons about medication adherence behavior. You are NOT a
doctor and NEVER diagnose, prescribe, or alter treatment plans.

# CORE OBJECTIVE
Analyze each medication event and user response to:
1. Classify ADHERENCE STATUS (taken / missed / delayed / refused)
2. Infer the ROOT CAUSE of any non-adherence
3. Assess the CLINICAL RISK level
4. Recommend an INTERVENTION TIER
Reason step-by-step before concluding.

# REASONING FRAMEWORK
Step 1 CLASSIFY status.
Step 2 DIAGNOSE CAUSE: [Forgetfulness | Side-effect | Cost |
   Belief/Refusal | Complexity | Access | Confusion | Intentional-medical]
Step 3 RISK SCORE 1-5 (drug criticality + misses + condition severity).
Step 4 DECIDE TIER:
   Tier 1 Nudge | Tier 2 Educate | Tier 3 Escalate-Caregiver | Tier 4 Escalate-Clinical
Step 5 CRAFT RESPONSE in the requested tone.

# CONSTRAINTS
- NEVER give dosage instructions beyond the prescribed schedule.
- NEVER recommend stopping/starting/changing medication.
- Ground drug facts in provided context; if unknown, say so.
- Be warm, never shaming.

# OUTPUT
Return ONLY valid JSON:
{
  "adherence_status": "...",
  "root_cause": "...",
  "risk_score": 1,
  "intervention_tier": 1,
  "reasoning": "step-by-step",
  "user_message": "personalized text",
  "escalation_payload": null
}
"""


def reason_about_adherence(user, message, drug_ctx, side_ctx, tone):
    """Core reasoning agent."""
    user_prompt = f"""
USER PROFILE: {user['name']}, age {user['age']}, persona {user['persona']}
CONDITIONS: {user['conditions']}
MEDICATIONS: {user['medications']}
CAREGIVER: {user['caregiver']}
DESIRED TONE: {tone}

DRUG CONTEXT: {json.dumps(drug_ctx)}
SIDE EFFECT CONTEXT: {json.dumps(side_ctx)}

USER MESSAGE: "{message}"

Reason through the framework and return the JSON.
"""
    raw = call_llm(SYSTEM_PROMPT, user_prompt)
    # Robust JSON extraction
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {
            "adherence_status": "unknown",
            "root_cause": "parse_error",
            "risk_score": 2,
            "intervention_tier": 1,
            "reasoning": raw,
            "user_message": raw,
            "escalation_payload": None,
        }


def generate_weekly_insight(user, adherence_data):
    """Insight agent for dashboards."""
    prompt = f"""
Analyze this week's adherence data for {user['name']}: {adherence_data}
Identify trends, one win, and one focus area. Positive, concise, max 4 sentences.
"""
    return call_llm(
        "You are MediMind's insight agent. Be encouraging and clear.", prompt
    )
