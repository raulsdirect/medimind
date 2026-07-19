# MediMind 💊🧠
### Intelligent AI Health Adherence Companion

MediMind reasons about *why* patients miss medications and intervenes 
intelligently — going far beyond simple reminders.

## 🎯 Key Features
- **Multi-agent AI reasoning** (Claude / GPT powered)
- **Root-cause analysis** of non-adherence
- **Tiered intervention** (nudge → educate → caregiver → clinical)
- **Emergency override** for critical symptoms
- **Safety guardrails** — never prescribes or changes doses
- **Transparent reasoning** view + adherence dashboard

## 🏗️ Architecture
Orchestrator routes each message → Guardrail check → Knowledge Base 
grounding → Reasoning Agent → Escalation logic → Personalized response.

## 🚀 Setup
1. `git clone <repo> && cd medimind`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and add your API key
4. `streamlit run app.py`
5. Open http://localhost:8501

## 🧪 Try These Demos
- Robert: "I forgot my evening dose again" → Tier 1 adaptive nudge
- Maria: "I stopped my statin, my legs ache" → Tier 2 + escalation
- Robert: "I took my heart pill but my chest feels tight" → 🚨 Emergency

## ⚠️ Disclaimer
MediMind is not a medical device. It does not diagnose or prescribe. 
Always consult healthcare professionals.

## 📄 License
MIT
