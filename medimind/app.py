import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from backend.orchestrator import process_message, weekly_report

st.set_page_config(page_title="MediMind 💊🧠", page_icon="💊", layout="wide")

# --- Path setup (works on Streamlit Cloud) ---
BASE_DIR = Path(__file__).parent

# --- Load users ---
with open(BASE_DIR / "data" / "users.json") as f:
    USERS = json.load(f)

# --- Sidebar ---
st.sidebar.title("💊 MediMind")
st.sidebar.caption("AI That Understands *Why* You Miss")
user_key = st.sidebar.selectbox("Select user profile", list(USERS.keys()),
                                format_func=lambda k: USERS[k]["name"])
user = USERS[user_key]

st.sidebar.markdown("### 👤 Profile")
st.sidebar.write(f"**{user['name']}**, age {user['age']}")
st.sidebar.write(f"**Persona:** {user['persona']}")
st.sidebar.write(f"**Conditions:** {', '.join(user['conditions'])}")
st.sidebar.write(f"**Medications:** {', '.join(user['medications'])}")
st.sidebar.write(f"**Caregiver:** {user['caregiver'] or 'None'}")

tab1, tab2, tab3 = st.tabs(["💬 Adherence Chat", "📊 Dashboard", "🧠 AI Reasoning"])

# --- Session state ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# =========== TAB 1: CHAT ===========
with tab1:
    st.header("Adherence Companion")
    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.write(msg)

    if prompt := st.chat_input("Type your response (e.g., 'I forgot my evening dose')"):
        st.session_state.chat.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("MediMind is reasoning..."):
            result = process_message(user, prompt)
            st.session_state.last_result = result

        with st.chat_message("assistant"):
            st.write(result["user_message"])
            tier = result.get("intervention_tier", 1)
            colors = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}
            st.caption(
                f"{colors.get(tier,'⚪')} Tier {tier} · "
                f"Risk {result.get('risk_score')}/5 · "
                f"Cause: {result.get('root_cause')}"
            )
            if result.get("escalation_payload"):
                st.warning(f"⚠️ Escalation triggered: {result['escalation_payload']}")

        st.session_state.chat.append(("assistant", result["user_message"]))

# =========== TAB 2: DASHBOARD ===========
with tab2:
    st.header("📊 Adherence Dashboard")
    demo_data = {"Mon": 100, "Tue": 100, "Wed": 66, "Thu": 100,
                 "Fri": 33, "Sat": 100, "Sun": 66}
    df = pd.DataFrame({"Day": list(demo_data.keys()),
                       "Adherence %": list(demo_data.values())})

    fig = go.Figure(go.Bar(x=df["Day"], y=df["Adherence %"],
                           marker_color=["#2ecc71" if v >= 80 else "#f39c12" if v >= 50
                                         else "#e74c3c" for v in df["Adherence %"]]))
    fig.update_layout(title="Weekly Adherence", yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Weekly Adherence", "81%", "+6%")
    col2.metric("Doses Taken", "17/21")
    col3.metric("Risk Level", "Moderate")

    if st.button("Generate AI Weekly Insight"):
        with st.spinner("Analyzing..."):
            insight = weekly_report(user, demo_data)
        st.success(insight)

# =========== TAB 3: REASONING ===========
with tab3:
    st.header("🧠 AI Decision Transparency")
    st.caption("This is the reasoning behind the last response — proves it's not a simple chatbot.")
    if st.session_state.last_result:
        st.json(st.session_state.last_result)
    else:
        st.info("Send a message in the Chat tab to see the AI's reasoning.")
