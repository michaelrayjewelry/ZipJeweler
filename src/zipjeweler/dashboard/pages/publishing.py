"""Page 5: Publishing — Post queue, platform health, schedule editor."""

import streamlit as st

from zipjeweler.dashboard.db import (
    get_db,
    get_recent_content,
    get_recent_engagements,
)
from zipjeweler.dashboard.components.data_tables import render_engagement_table


def page():
    st.title("Publishing — Post Queue & Platform Health")
    st.caption("Control posting schedule, monitor platform health, and manage the post queue.")
    st.markdown("---")

    with get_db() as session:
        content_items = get_recent_content(session, limit=50)
        engagements = get_recent_engagements(session, limit=50)

    # --- Post Queue ---
    approved = [c for c in content_items if c.status == "approved"]
    posted = [c for c in content_items if c.status == "posted"]

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Queued for Posting", len(approved))
    with col_m2:
        st.metric("Published Today", len(posted))
    with col_m3:
        st.metric("Total Published", len(engagements))

    st.markdown("---")

    # --- Tabs ---
    tab_queue, tab_published, tab_health, tab_schedule = st.tabs([
        "Post Queue", "Published Posts", "Platform Health", "Schedule",
    ])

    # --- Post Queue ---
    with tab_queue:
        st.subheader("Approved — Ready to Post")
        if not approved:
            st.success("Post queue is empty. Approve content to add it to the queue.")
        else:
            for content in approved:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{content.content_type.title()}** for **{content.target_platform}**")
                        st.text((content.final_text or content.text_draft or "")[:200])
                    with col2:
                        st.caption(f"Created: {content.created_at.strftime('%m/%d %H:%M') if content.created_at else '—'}")
                    with col3:
                        if st.button("Post Now", key=f"post_{content.id}", type="primary", use_container_width=True):
                            st.toast(f"Posting content #{content.id}...", icon="📤")
                        if st.button("Cancel", key=f"cancel_{content.id}", use_container_width=True):
                            st.toast(f"Post #{content.id} cancelled")

    # --- Published Posts ---
    with tab_published:
        st.subheader("Published Posts")
        render_engagement_table(engagements)

    # --- Platform Health ---
    with tab_health:
        st.subheader("Platform Health")

        platforms = [
            {"name": "Reddit", "api": "PRAW", "status": "connected", "rate_usage": 15},
            {"name": "Twitter/X", "api": "Tweepy", "status": "not_configured", "rate_usage": 0},
            {"name": "LinkedIn", "api": "OAuth REST", "status": "not_configured", "rate_usage": 0},
            {"name": "Instagram", "api": "Graph API", "status": "not_configured", "rate_usage": 0},
            {"name": "Facebook", "api": "Graph API", "status": "not_configured", "rate_usage": 0},
            {"name": "Pinterest", "api": "SDK v5", "status": "not_configured", "rate_usage": 0},
        ]

        for p in platforms:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{p['name']}**")
                    st.caption(f"API: {p['api']}")
                with col2:
                    if p["status"] == "connected":
                        st.success("Connected")
                    elif p["status"] == "error":
                        st.error("Error")
                    else:
                        st.warning("Not Configured")
                with col3:
                    st.caption(f"Rate: {p['rate_usage']}% used")
                    st.progress(p["rate_usage"] / 100)
                with col4:
                    st.button("Test", key=f"test_{p['name']}", use_container_width=True)

    # --- Schedule ---
    with tab_schedule:
        st.subheader("Posting Schedule")

        schedule_data = {
            "Reddit": {"times": ["14:00", "17:00", "21:00"], "days": "Mon-Thu", "max_per_hour": 5},
            "Twitter": {"times": ["13:00", "16:00", "20:00"], "days": "Tue-Thu", "max_per_hour": 5},
            "LinkedIn": {"times": ["12:00", "15:00"], "days": "Tue-Thu", "max_per_day": 2},
            "Instagram": {"times": ["14:00", "18:00", "21:00"], "days": "Mon, Wed, Fri", "max_per_day": 3},
            "Facebook": {"times": ["13:00", "16:00", "20:00"], "days": "Tue, Thu, Sat", "max_per_day": 3},
            "Pinterest": {"times": ["15:00", "20:00"], "days": "Fri-Sun", "max_per_day": 10},
        }

        for platform, sched in schedule_data.items():
            with st.expander(f"**{platform}** — {sched['days']}"):
                st.text(f"Optimal times (UTC): {', '.join(sched['times'])}")
                limit_key = "max_per_hour" if "max_per_hour" in sched else "max_per_day"
                limit_val = sched.get(limit_key, 5)
                st.number_input(
                    f"Max posts per {'hour' if 'hour' in limit_key else 'day'}",
                    1, 50, limit_val,
                    key=f"schedule_{platform}",
                )

    # --- Emergency Stop ---
    st.markdown("---")
    col_e1, col_e2 = st.columns([1, 3])
    with col_e1:
        if st.button("EMERGENCY STOP", type="primary", use_container_width=True):
            st.warning("All posting paused! Click Resume to continue.")
            st.session_state["posting_paused"] = True
    with col_e2:
        if st.session_state.get("posting_paused"):
            if st.button("Resume Posting", use_container_width=True):
                st.session_state["posting_paused"] = False
                st.toast("Posting resumed!", icon="▶️")
                st.rerun()
