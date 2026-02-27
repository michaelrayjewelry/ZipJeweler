"""Page 2: Listening — Leads feed, keyword management, topic weights."""

import streamlit as st

from zipjeweler.dashboard.db import (
    get_db,
    get_leads_by_platform,
    get_leads_by_status,
    get_leads_by_topic,
    get_recent_leads,
)
from zipjeweler.dashboard.components.charts import (
    render_platform_pie,
    render_score_distribution,
    render_status_bar,
    render_topic_bar,
)
from zipjeweler.dashboard.components.data_tables import render_leads_table


def page():
    st.title("Listening — Social Listening & Prospecting")
    st.caption("Discover leads across 6 platforms, qualify them, and manage keywords.")
    st.markdown("---")

    # --- Overview Charts ---
    with get_db() as session:
        platform_data = get_leads_by_platform(session)
        status_data = get_leads_by_status(session)
        topic_data = get_leads_by_topic(session)
        leads = get_recent_leads(session, limit=100)

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        render_platform_pie(platform_data, "Leads by Platform")
    with col_c2:
        render_status_bar(status_data, "Leads by Status")
    with col_c3:
        render_score_distribution(leads, "Lead Score Distribution")

    st.markdown("---")

    # --- Topic Distribution ---
    render_topic_bar(topic_data, "Leads by Topic Category")

    st.markdown("---")

    # --- Filters ---
    st.subheader("Lead Feed")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        platform_filter = st.selectbox(
            "Platform",
            ["All", "reddit", "twitter", "linkedin", "facebook", "instagram", "pinterest"],
            key="lead_platform_filter",
        )
    with col_f2:
        status_filter = st.selectbox(
            "Status",
            ["All", "new", "reply_drafted", "replied", "contacted", "converted", "dismissed"],
            key="lead_status_filter",
        )
    with col_f3:
        min_score = st.slider("Min Score", 0, 100, 0, key="lead_min_score")
    with col_f4:
        topic_filter = st.selectbox(
            "Topic",
            ["All", "cad_modelers", "jewelry_designers", "custom_jewelry_questions",
             "jewelry_production", "casting_issues", "looking_for_cad",
             "looking_for_designers", "looking_for_manufacturers", "business_management_pain"],
            key="lead_topic_filter",
        )

    # Apply filters
    filtered = leads
    if platform_filter != "All":
        filtered = [l for l in filtered if l.platform == platform_filter]
    if status_filter != "All":
        filtered = [l for l in filtered if l.status == status_filter]
    if min_score > 0:
        filtered = [l for l in filtered if l.lead_score >= min_score]
    if topic_filter != "All":
        filtered = [l for l in filtered if l.topic_category == topic_filter]

    st.caption(f"Showing {len(filtered)} of {len(leads)} leads")
    render_leads_table(filtered)

    # --- Platform Toggle ---
    st.markdown("---")
    st.subheader("Platform Controls")
    platforms = {
        "Reddit": True, "Twitter/X": True, "LinkedIn": True,
        "Facebook": True, "Instagram": True, "Pinterest": True,
    }
    cols = st.columns(6)
    for col, (name, enabled) in zip(cols, platforms.items()):
        with col:
            st.toggle(name, value=enabled, key=f"platform_toggle_{name}")

    # --- Keyword Manager ---
    st.markdown("---")
    st.subheader("Active Keywords")
    keyword_categories = {
        "CAD/Design": ["jewelry CAD", "MatrixGold", "Rhino jewelry", "3D jewelry model", "CAD rendering jewelry"],
        "Production": ["jewelry production", "lost wax casting", "casting defects", "jewelry manufacturing"],
        "Business": ["jewelry inventory management", "jewelry CRM", "jewelry business software", "jewelry POS"],
        "Custom Work": ["custom ring", "bespoke jewelry", "commission jewelry", "custom engagement ring"],
    }

    for cat, keywords in keyword_categories.items():
        with st.expander(f"**{cat}** ({len(keywords)} keywords)"):
            for kw in keywords:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(kw)
                with col2:
                    st.checkbox("Active", value=True, key=f"kw_{kw}", label_visibility="collapsed")

    # --- Quick Actions ---
    st.markdown("---")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("Run Listening Now", type="primary", use_container_width=True):
            st.toast("Listening crew started!", icon="👂")
    with col_a2:
        if st.button("Refresh Lead Scores", use_container_width=True):
            st.toast("Lead re-scoring started!", icon="🔄")
