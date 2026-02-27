"""Page 3: Engagement — Reply queue, nurture pipeline, tone config."""

import streamlit as st

from zipjeweler.dashboard.db import (
    get_db,
    get_leads_by_nurture_stage,
    get_recent_content,
    get_recent_leads,
)
from zipjeweler.dashboard.components.approval_widget import render_approval_queue
from zipjeweler.dashboard.components.charts import render_funnel_chart


def page():
    st.title("Engagement — Reply & Comment Management")
    st.caption("Manage replies, nurture sequences, and engagement tone per platform.")
    st.markdown("---")

    # --- Nurture Funnel ---
    with get_db() as session:
        funnel_data = get_leads_by_nurture_stage(session)
        content_items = get_recent_content(session, limit=50)
        leads = get_recent_leads(session, limit=50)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        render_funnel_chart(funnel_data, "Lead Nurture Funnel")

    with col_right:
        # Reply stats
        reply_drafts = [c for c in content_items if c.content_type == "reply" and c.status == "draft"]
        reply_approved = [c for c in content_items if c.content_type == "reply" and c.status == "approved"]
        reply_posted = [c for c in content_items if c.content_type == "reply" and c.status == "posted"]

        st.subheader("Reply Pipeline")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Pending", len(reply_drafts))
        with col_m2:
            st.metric("Approved", len(reply_approved))
        with col_m3:
            st.metric("Posted", len(reply_posted))

        # Engagement rules
        st.markdown("---")
        st.subheader("Engagement Rules")
        st.number_input("Max replies per day (all platforms)", 1, 100, 30, key="max_replies_day")
        st.number_input("Min lead score to engage", 0, 100, 70, key="min_engage_score")
        st.number_input("Max replies per thread", 1, 5, 1, key="max_thread_replies")

    st.markdown("---")

    # --- Reply Approval Queue ---
    st.subheader("Reply Approval Queue")
    replies = [c for c in content_items if c.content_type == "reply"]
    render_approval_queue(replies)

    # --- Tone Configurator ---
    st.markdown("---")
    st.subheader("Platform Tone Configuration")

    tone_settings = {
        "Reddit": {"casual": 80, "direct": 30, "humorous": 20},
        "Twitter/X": {"casual": 70, "direct": 50, "humorous": 30},
        "LinkedIn": {"casual": 20, "direct": 40, "humorous": 5},
        "Facebook": {"casual": 60, "direct": 40, "humorous": 20},
        "Instagram": {"casual": 75, "direct": 35, "humorous": 25},
        "Pinterest": {"casual": 50, "direct": 30, "humorous": 10},
    }

    for platform, defaults in tone_settings.items():
        with st.expander(f"**{platform}** Tone"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.slider(
                    "Casual vs Professional",
                    0, 100, defaults["casual"],
                    key=f"tone_casual_{platform}",
                    help="0 = Very Professional, 100 = Very Casual",
                )
            with col2:
                st.slider(
                    "Subtle vs Direct",
                    0, 100, defaults["direct"],
                    key=f"tone_direct_{platform}",
                    help="0 = Very Subtle mention, 100 = Direct pitch",
                )
            with col3:
                st.slider(
                    "Serious vs Humorous",
                    0, 100, defaults["humorous"],
                    key=f"tone_humor_{platform}",
                    help="0 = Very Serious, 100 = Humorous",
                )

    # --- Nurture Stage Detail ---
    st.markdown("---")
    st.subheader("Leads by Nurture Stage")

    stage_tabs = st.tabs([
        "Discovery", "First Touch", "Follow-Up",
        "Soft Pitch", "Conversion", "Post-Conversion",
    ])

    stage_names = ["discovery", "first_touch", "follow_up", "soft_pitch", "conversion", "post_conversion"]
    for tab, stage in zip(stage_tabs, stage_names):
        with tab:
            stage_leads = [l for l in leads if l.nurture_stage == stage]
            if stage_leads:
                for lead in stage_leads[:10]:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{lead.author}** ({lead.platform}) — Score: {lead.lead_score}")
                            st.caption((lead.content_snippet or "")[:150])
                        with col2:
                            st.caption(f"Status: {lead.status}")
            else:
                st.caption(f"No leads at {stage.replace('_', ' ')} stage")
