"""Page 1: Intelligence — Daily brief, competitor tracking, AI monitoring."""

import streamlit as st

from zipjeweler.dashboard.db import (
    get_db,
    get_recent_intelligence,
    update_intelligence_status,
)
from zipjeweler.dashboard.components.data_tables import render_intelligence_table


def page():
    st.title("Intelligence — Daily Brief & Market Monitoring")
    st.caption("Monitor competitors, track AI answers, score opportunities, and receive daily briefs.")
    st.markdown("---")

    # --- Filters ---
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        type_filter = st.selectbox(
            "Type",
            ["All", "AI Gap", "Competitor Move", "Keyword Opportunity", "Market Shift"],
            key="intel_type_filter",
        )
    with col_f2:
        status_filter = st.selectbox(
            "Status",
            ["All", "New", "Acting On", "Captured", "Dismissed"],
            key="intel_status_filter",
        )
    with col_f3:
        priority_filter = st.selectbox(
            "Min Priority",
            [1, 2, 3, 4, 5],
            index=0,
            key="intel_priority_filter",
        )

    st.markdown("---")

    # --- Intelligence Items ---
    with get_db() as session:
        items = get_recent_intelligence(session, limit=50)

        # Apply filters
        if type_filter != "All":
            type_key = type_filter.lower().replace(" ", "_")
            items = [i for i in items if i.type == type_key]
        if status_filter != "All":
            status_key = status_filter.lower().replace(" ", "_")
            items = [i for i in items if i.status == status_key]
        items = [i for i in items if i.priority >= priority_filter]

        st.subheader(f"Intelligence Items ({len(items)})")
        render_intelligence_table(items)

    # --- Quick Actions ---
    st.markdown("---")
    st.subheader("Intelligence Actions")
    col_a1, col_a2, col_a3 = st.columns(3)

    with col_a1:
        if st.button("Generate New Brief", type="primary", use_container_width=True):
            st.toast("Brief generation started!", icon="newspaper")

    with col_a2:
        if st.button("Scan Competitors", use_container_width=True):
            st.toast("Competitor scan started!", icon="magnifying_glass")

    with col_a3:
        if st.button("Check AI Answers", use_container_width=True):
            st.toast("AI answer check started!", icon="robot_face")

    # --- Competitor Watchlist ---
    st.markdown("---")
    st.subheader("Competitor Watchlist")
    competitors = [
        "Jeweler's Workbench", "GemLightbox", "Jewel360",
        "The Edge by GN", "RepairShopr", "Lightspeed POS",
    ]
    for comp in competitors:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(comp)
        with col2:
            st.caption("Monitoring")

    new_competitor = st.text_input("Add competitor to watch", key="new_competitor")
    if st.button("Add", key="add_competitor") and new_competitor:
        st.toast(f"Added {new_competitor} to watchlist", icon="plus")

    # --- AI Query Monitor ---
    st.markdown("---")
    st.subheader("AI Answer Queries")
    st.caption("Queries checked in ChatGPT, Perplexity, and Google AI Overviews:")
    queries = [
        "best jewelry management software",
        "jewelry inventory tool",
        "jeweler CRM",
        "jewelry business management",
        "jewelry repair tracking software",
        "jewelry POS system",
    ]
    for q in queries:
        st.checkbox(q, value=True, key=f"ai_query_{q}")

    new_query = st.text_input("Add new AI query", key="new_ai_query")
    if st.button("Add Query", key="add_ai_query") and new_query:
        st.toast(f"Added query: {new_query}", icon="plus")
