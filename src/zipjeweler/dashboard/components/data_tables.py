"""Filterable, sortable data tables for dashboard pages."""

from datetime import datetime

import streamlit as st


def _format_datetime(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%Y-%m-%d %H:%M")


def render_leads_table(leads: list, show_actions: bool = True):
    """Render a table of leads with optional action buttons."""
    if not leads:
        st.info("No leads found yet. Run the Listening Crew to discover leads.")
        return

    for lead in leads:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(f"**{lead.author}** on **{lead.platform}**")
                snippet = (lead.content_snippet or "")[:200]
                st.caption(snippet)
                if lead.source_url:
                    st.caption(f"[View source]({lead.source_url})")

            with col2:
                score_color = "green" if lead.lead_score >= 70 else "orange" if lead.lead_score >= 50 else "red"
                st.markdown(f"Score: **:{score_color}[{lead.lead_score}]**")
                st.caption(f"${lead.dollar_value:.0f} est. value")

            with col3:
                st.caption(f"Topic: {lead.topic_category}")
                st.caption(f"Stage: {lead.nurture_stage}")
                st.caption(f"Status: {lead.status}")

            with col4:
                st.caption(_format_datetime(lead.created_at))
                if show_actions:
                    if lead.status == "new":
                        if st.button("Draft Reply", key=f"draft_{lead.id}", use_container_width=True):
                            st.toast(f"Reply draft queued for lead #{lead.id}")


def render_content_table(contents: list, show_actions: bool = True):
    """Render content items with approval actions."""
    if not contents:
        st.info("No content created yet. Run the Content Crew to generate content.")
        return

    for content in contents:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                type_label = content.content_type.replace("_", " ").title()
                st.markdown(f"**{type_label}** for **{content.target_platform}**")
                text = content.final_text or content.text_draft or ""
                st.text(text[:300] + ("..." if len(text) > 300 else ""))
                if content.strategy_notes:
                    st.caption(f"Strategy: {content.strategy_notes}")

            with col2:
                status_map = {
                    "draft": ("Draft", "orange"),
                    "approved": ("Approved", "green"),
                    "rejected": ("Rejected", "red"),
                    "edited": ("Edited", "blue"),
                    "posted": ("Posted", "green"),
                }
                label, color = status_map.get(content.status, ("Unknown", "gray"))
                st.markdown(f":{color}[{label}]")
                if content.ab_variant:
                    st.caption(f"A/B: Variant {content.ab_variant}")

            with col3:
                st.caption(_format_datetime(content.created_at))
                if show_actions and content.status == "draft":
                    if st.button("Approve", key=f"approve_{content.id}", type="primary", use_container_width=True):
                        st.session_state[f"action_{content.id}"] = "approved"
                        st.rerun()
                    if st.button("Reject", key=f"reject_{content.id}", use_container_width=True):
                        st.session_state[f"action_{content.id}"] = "rejected"
                        st.rerun()


def render_intelligence_table(items: list):
    """Render intelligence brief items."""
    if not items:
        st.info("No intelligence data yet. Run the Intelligence Crew to generate a daily brief.")
        return

    for item in items:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                type_label = item.type.replace("_", " ").title()
                priority_stars = "!" * item.priority
                st.markdown(f"**[P{item.priority}]** {type_label}")
                st.write(item.description)
                if item.draft_content:
                    with st.expander("View draft content"):
                        st.text(item.draft_content)

            with col2:
                if item.dollar_value > 0:
                    st.metric("Est. Value", f"${item.dollar_value:,.0f}")
                if item.competitor:
                    st.caption(f"Competitor: {item.competitor}")
                st.caption(f"Source: {item.source or 'Auto-detected'}")

            with col3:
                status_map = {
                    "new": "New",
                    "acting_on": "Acting On",
                    "captured": "Captured",
                    "dismissed": "Dismissed",
                }
                st.caption(f"Status: {status_map.get(item.status, item.status)}")
                st.caption(f"Date: {item.date}")


def render_engagement_table(engagements: list):
    """Render published post engagement data."""
    if not engagements:
        st.info("No engagement data yet. Publish content to start tracking performance.")
        return

    for eng in engagements:
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.caption(f"**{eng.platform}** — {eng.post_type}")
                if eng.post_url:
                    st.caption(f"[View post]({eng.post_url})")

            with col2:
                st.metric("Likes", eng.likes)
            with col3:
                st.metric("Shares", eng.shares)
            with col4:
                st.metric("Comments", eng.comments)
            with col5:
                st.metric("Clicks", eng.clicks)


def render_learnings_table(learnings: list):
    """Render learning insights."""
    if not learnings:
        st.info("No insights yet. The Analytics Crew will extract learnings from engagement data.")
        return

    for learn in learnings:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"**[{learn.category.title()}]** {learn.insight}")
                if learn.evidence:
                    st.caption(f"Evidence: {learn.evidence}")

            with col2:
                conf_color = "green" if learn.confidence >= 70 else "orange" if learn.confidence >= 40 else "red"
                st.markdown(f"Confidence: :{conf_color}[{learn.confidence:.0f}%]")
                st.caption(f"Applied: {'Yes' if learn.applied else 'No'}")
                st.caption(_format_datetime(learn.last_validated))
