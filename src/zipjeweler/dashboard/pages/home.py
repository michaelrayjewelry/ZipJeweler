"""Page 0: Home — System overview, KPIs, activity feed, quick actions."""

import streamlit as st

from zipjeweler.dashboard.db import (
    count_content_created_today,
    count_leads_today,
    count_leads_yesterday,
    count_posts_published_today,
    count_replies_drafted,
    get_db,
    get_leads_by_platform,
    get_total_engagement,
)
from zipjeweler.dashboard.components.agent_status import render_crew_status_panel
from zipjeweler.dashboard.components.charts import render_platform_pie
from zipjeweler.dashboard.components.metric_cards import render_kpi_cards


def page():
    st.title("ZipJeweler Agent Management")
    st.markdown("---")

    # --- KPI Metrics ---
    with get_db() as session:
        leads_today = count_leads_today(session)
        leads_yesterday = count_leads_yesterday(session)
        replies = count_replies_drafted(session)
        content = count_content_created_today(session)
        posts = count_posts_published_today(session)
        total_eng = get_total_engagement(session)
        platform_data = get_leads_by_platform(session)

    delta = leads_today - leads_yesterday if leads_yesterday > 0 else None
    render_kpi_cards(leads_today, delta, replies, content, posts, total_eng)

    st.markdown("---")

    # --- Platform Overview + Crew Status ---
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Leads by Platform")
        render_platform_pie(platform_data)

    with col_right:
        st.subheader("Crew Status")
        render_crew_status_panel()

    st.markdown("---")

    # --- Quick Actions ---
    st.subheader("Quick Actions")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)

    with col_q1:
        if st.button("Run Full Pipeline", type="primary", use_container_width=True):
            st.toast("Full pipeline started! Check crew status for progress.", icon="rocket")

    with col_q2:
        if st.button("Generate Daily Brief", use_container_width=True):
            st.toast("Daily brief generation started!", icon="newspaper")

    with col_q3:
        if st.button("Run Listening", use_container_width=True):
            st.toast("Listening crew started!", icon="ear")

    with col_q4:
        if st.button("Pause All Agents", use_container_width=True):
            if "crew_statuses" in st.session_state:
                for k in st.session_state.crew_statuses:
                    st.session_state.crew_statuses[k] = "idle"
            st.toast("All agents paused", icon="stop_sign")
            st.rerun()

    # --- System Info ---
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.caption("Mode: **DRY RUN** (no live posts)")
    with col_info2:
        st.caption("Approval: **Human Required**")
    with col_info3:
        st.caption("ZipJeweler Agents v0.1")
