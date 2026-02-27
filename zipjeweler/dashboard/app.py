"""ZipJeweler Dashboard — Streamlit management console."""
import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="ZipJeweler Command Center",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=ZipJeweler", width=200)
    st.markdown("## ⚙️ Control Panel")

    autonomy = st.select_slider(
        "Autonomy Level",
        options=["Supervised", "Semi-Auto", "Autonomous"],
        value="Supervised",
    )

    dry_run = st.toggle("Dry Run Mode", value=True)

    st.markdown("---")
    st.markdown("### Quick Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Brief", use_container_width=True):
            st.session_state["action"] = "brief"
    with col2:
        if st.button("👂 Listen", use_container_width=True):
            st.session_state["action"] = "listen"

    col3, col4 = st.columns(2)
    with col3:
        if st.button("💬 Engage", use_container_width=True):
            st.session_state["action"] = "engage"
    with col4:
        if st.button("🚀 Full Run", use_container_width=True):
            st.session_state["action"] = "run"

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ── Main ─────────────────────────────────────────────────────────────────────
st.title("💎 ZipJeweler Command Center")
st.caption("36 autonomous agents · 7 crews · One mission: grow your business")

# ── Crew Status Cards ────────────────────────────────────────────────────────
st.subheader("🤖 Crew Status")

crews = [
    {"name": "Intelligence", "icon": "🔍", "agents": 4, "status": "idle", "last_run": "Never"},
    {"name": "Listening",    "icon": "👂", "agents": 7, "status": "idle", "last_run": "Never"},
    {"name": "Engagement",   "icon": "💬", "agents": 7, "status": "idle", "last_run": "Never"},
    {"name": "Content",      "icon": "✍️",  "agents": 3, "status": "idle", "last_run": "Never"},
    {"name": "Posting",      "icon": "📤", "agents": 6, "status": "idle", "last_run": "Never"},
    {"name": "Analytics",    "icon": "📊", "agents": 3, "status": "idle", "last_run": "Never"},
    {"name": "Evolution",    "icon": "🧬", "agents": 7, "status": "idle", "last_run": "Never"},
]

cols = st.columns(4)
for i, crew in enumerate(crews):
    with cols[i % 4]:
        status_color = {"idle": "🟡", "running": "🟢", "error": "🔴"}.get(crew["status"], "🟡")
        st.metric(
            label=f"{crew['icon']} {crew['name']}",
            value=f"{crew['agents']} agents",
            delta=f"{status_color} {crew['status']}",
        )

st.markdown("---")

# ── Platform Connections ─────────────────────────────────────────────────────
st.subheader("🔗 Platform Connections")

platforms = {
    "Reddit": {"icon": "🟠", "connected": False},
    "Twitter/X": {"icon": "🐦", "connected": False},
    "LinkedIn": {"icon": "💼", "connected": False},
    "Instagram": {"icon": "📸", "connected": False},
    "Facebook": {"icon": "👥", "connected": False},
    "Pinterest": {"icon": "📌", "connected": False},
}

pcols = st.columns(6)
for i, (platform, info) in enumerate(platforms.items()):
    with pcols[i]:
        status = "✅ Connected" if info["connected"] else "❌ Not connected"
        st.metric(label=f"{info['icon']} {platform}", value=status)

st.markdown("---")

# ── Lead Funnel ──────────────────────────────────────────────────────────────
st.subheader("🎯 Lead Funnel")

funnel_cols = st.columns(6)
funnel_stages = [
    ("Discovery", 0),
    ("Awareness", 0),
    ("Interest", 0),
    ("Consideration", 0),
    ("Decision", 0),
    ("Conversion", 0),
]
for i, (stage, count) in enumerate(funnel_stages):
    with funnel_cols[i]:
        st.metric(label=stage, value=count)

st.markdown("---")

# ── Activity Feed ────────────────────────────────────────────────────────────
st.subheader("📡 Activity Feed")

if "activity" not in st.session_state:
    st.session_state["activity"] = []

if st.session_state.get("action"):
    action = st.session_state.pop("action")
    log = f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Command dispatched: **{action}** (dry_run={dry_run})"
    st.session_state["activity"].insert(0, log)
    st.success(f"Command sent: `{action}` — check terminal for output")

if st.session_state["activity"]:
    for entry in st.session_state["activity"][:20]:
        st.markdown(entry)
else:
    st.info("No activity yet. Use Quick Actions to run your first agent command.")

st.markdown("---")

# ── Configuration ────────────────────────────────────────────────────────────
with st.expander("⚙️ Configuration & API Keys"):
    st.markdown("Edit your `.env` file to configure API keys:")
    env_keys = [
        "ANTHROPIC_API_KEY", "REDDIT_CLIENT_ID", "TWITTER_BEARER_TOKEN",
        "INSTAGRAM_USERNAME", "LINKEDIN_ACCESS_TOKEN", "GOOGLE_SHEETS_SPREADSHEET_ID"
    ]
    for key in env_keys:
        val = os.getenv(key, "")
        masked = ("*" * 8 + val[-4:]) if len(val) > 4 else ("Not set" if not val else val)
        st.text_input(key, value=masked, disabled=True)

    st.markdown("Run `cp .env.example .env` and fill in your API keys to connect platforms.")
