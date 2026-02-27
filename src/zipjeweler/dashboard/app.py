"""ZipJeweler Agent Management Dashboard — Main entry point.

Launch with: streamlit run src/zipjeweler/dashboard/app.py
"""

import sys
from pathlib import Path

# Ensure the src directory is on the Python path
_src_dir = str(Path(__file__).resolve().parents[2])
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import streamlit as st

# --- Page Config (must be first Streamlit call) ---
st.set_page_config(
    page_title="ZipJeweler Agents",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Ensure DB tables exist ---
from zipjeweler.dashboard.db import ensure_tables

ensure_tables()

# --- Import page modules ---
from zipjeweler.dashboard.pages.home import page as home_page
from zipjeweler.dashboard.pages.intelligence import page as intelligence_page
from zipjeweler.dashboard.pages.listening import page as listening_page
from zipjeweler.dashboard.pages.engagement import page as engagement_page
from zipjeweler.dashboard.pages.content import page as content_page
from zipjeweler.dashboard.pages.publishing import page as publishing_page
from zipjeweler.dashboard.pages.analytics import page as analytics_page
from zipjeweler.dashboard.pages.evolution import page as evolution_page
from zipjeweler.dashboard.pages.settings import page as settings_page

# --- Navigation ---
pages = {
    "Home": home_page,
    "Intelligence": intelligence_page,
    "Listening": listening_page,
    "Engagement": engagement_page,
    "Content": content_page,
    "Publishing": publishing_page,
    "Analytics": analytics_page,
    "Evolution": evolution_page,
    "Settings": settings_page,
}

# Sidebar navigation
with st.sidebar:
    st.markdown("### 💎 ZipJeweler Agents")

    page_labels = {
        "Home": "🏠 Home",
        "Intelligence": "🧠 Intelligence",
        "Listening": "👂 Listening",
        "Engagement": "💬 Engagement",
        "Content": "📝 Content",
        "Publishing": "📤 Publishing",
        "Analytics": "📊 Analytics",
        "Evolution": "🧬 Evolution",
        "Settings": "⚙️ Settings",
    }

    selected = st.radio(
        "Go to",
        list(pages.keys()),
        format_func=lambda x: page_labels.get(x, x),
        label_visibility="collapsed",
    )

    st.markdown("---")

    # System status summary
    from zipjeweler.dashboard.api.crew_controller import get_all_crew_states

    states = get_all_crew_states()
    running = sum(1 for s in states.values() if s.value == "running")
    errored = sum(1 for s in states.values() if s.value == "error")

    if running > 0:
        st.success(f"{running} crew(s) running")
    if errored > 0:
        st.error(f"{errored} crew(s) with errors")
    if running == 0 and errored == 0:
        st.info("All crews idle")

    st.markdown("---")
    st.caption("ZipJeweler Agents v0.1")
    st.caption("by Michael Ray Jewelry")

# --- Render selected page ---
pages[selected]()
