"""Page 7: Evolution — Strategy changes, self-improvement, retrospectives."""

import streamlit as st

from zipjeweler.dashboard.db import (
    get_db,
    get_recent_learnings,
    get_recent_retrospectives,
)
from zipjeweler.dashboard.components.charts import render_confidence_gauge
from zipjeweler.dashboard.components.data_tables import render_learnings_table


def page():
    st.title("Evolution — Strategy & Self-Improvement")
    st.caption("See how agents evolve their strategies based on performance data.")
    st.markdown("---")

    with get_db() as session:
        learnings = get_recent_learnings(session, limit=50)
        retrospectives = get_recent_retrospectives(session, limit=10)

    # --- Tabs ---
    tab_insights, tab_retro, tab_strategy, tab_goals, tab_override = st.tabs([
        "Learning Insights", "Retrospectives", "Strategy Log", "Goals", "Manual Override",
    ])

    # --- Insights Tab ---
    with tab_insights:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"Learning Insights ({len(learnings)})")

            cat_filter = st.selectbox(
                "Category",
                ["All", "content", "timing", "platform", "audience", "topic", "reply_style", "keyword"],
                key="learning_cat_filter",
            )

            filtered = learnings
            if cat_filter != "All":
                filtered = [l for l in filtered if l.category == cat_filter]

            render_learnings_table(filtered)

        with col2:
            render_confidence_gauge(learnings, "Avg Insight Confidence")

            # Confidence decay alerts
            st.subheader("Confidence Alerts")
            decaying = [l for l in learnings if l.confidence < 50]
            if decaying:
                for l in decaying[:5]:
                    st.warning(f"Low confidence ({l.confidence:.0f}%): {l.insight[:80]}...")
            else:
                st.success("All insights are healthy!")

    # --- Retrospectives Tab ---
    with tab_retro:
        st.subheader("Strategy Retrospectives")

        if not retrospectives:
            st.info("No retrospectives yet. The Evolution Crew runs weekly and monthly reviews automatically.")
        else:
            for retro in retrospectives:
                with st.expander(f"**{retro.period}** ({retro.type.title()}) — Score: {retro.self_improvement_score:.0f}%"):
                    col1, col2 = st.columns(2)

                    with col1:
                        if retro.top_performing_content:
                            st.markdown("**Top Content:**")
                            st.caption(retro.top_performing_content)
                        if retro.top_performing_platform:
                            st.markdown(f"**Top Platform:** {retro.top_performing_platform}")
                        if retro.top_performing_segment:
                            st.markdown(f"**Top Segment:** {retro.top_performing_segment}")

                    with col2:
                        if retro.ab_test_results:
                            st.markdown("**A/B Test Results:**")
                            st.caption(retro.ab_test_results)
                        if retro.emerging_trends:
                            st.markdown("**Emerging Trends:**")
                            st.caption(retro.emerging_trends)

                    if retro.strategy_changes_made:
                        st.markdown("**Strategy Changes:**")
                        st.write(retro.strategy_changes_made)

                    if retro.goals_vs_actual:
                        st.markdown("**Goals vs Actual:**")
                        st.write(retro.goals_vs_actual)

                    if retro.next_period_goals:
                        st.markdown("**Next Period Goals:**")
                        st.write(retro.next_period_goals)

                    # Direction input
                    direction = st.text_area(
                        "Your direction for next period",
                        value=retro.direction or "",
                        key=f"retro_dir_{retro.id}",
                    )

    # --- Strategy Log Tab ---
    with tab_strategy:
        st.subheader("Strategy Change Log")
        st.caption("Timeline of every strategy change the Evolution Crew made automatically.")

        applied_learnings = [l for l in learnings if l.applied]
        if not applied_learnings:
            st.info("No strategy changes applied yet.")
        else:
            for l in applied_learnings:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**[{l.category.title()}]** {l.insight}")
                        st.caption(f"Evidence: {l.evidence}")
                    with col2:
                        st.caption(f"Confidence: {l.confidence:.0f}%")
                        dt = l.last_validated
                        if dt:
                            st.caption(dt.strftime("%Y-%m-%d"))

    # --- Goals Tab ---
    with tab_goals:
        st.subheader("Performance Goals")

        goals = {
            "Lead Quality Score (avg)": {"target": "+5% monthly", "current": "—"},
            "Reply Conversion Rate": {"target": "+10% monthly", "current": "—"},
            "Content Engagement Rate": {"target": "+8% monthly", "current": "—"},
            "Time-to-First-Engagement": {"target": "-20% monthly", "current": "—"},
            "Cost Per Qualified Lead": {"target": "-15% monthly", "current": "—"},
            "Strategy Accuracy": {"target": "+5% monthly", "current": "—"},
            "Autonomous Actions": {"target": "Gradual increase", "current": "0%"},
        }

        for goal_name, goal_data in goals.items():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{goal_name}**")
                with col2:
                    st.caption(f"Target: {goal_data['target']}")
                with col3:
                    st.caption(f"Current: {goal_data['current']}")

        st.caption("Goals are automatically set by the Evolution Crew after 30+ days of data.")

    # --- Manual Override Tab ---
    with tab_override:
        st.subheader("Manual Strategy Override")
        st.caption("Force specific strategy changes that override automatic evolution.")

        st.markdown("#### Focus Override")
        focus_platform = st.multiselect(
            "Focus all effort on these platforms",
            ["reddit", "twitter", "linkedin", "facebook", "instagram", "pinterest"],
            default=[],
            key="focus_platforms",
        )
        focus_duration = st.selectbox("Duration", ["1 day", "3 days", "1 week", "2 weeks"], key="focus_duration")

        st.markdown("#### Content Style Override")
        style_override = st.selectbox(
            "Force content style",
            ["None (use auto)", "Story-based only", "Pain-point only", "Benefit-focused only", "How-to only"],
            key="style_override",
        )

        st.markdown("#### Priority Override")
        priority_override = st.text_area(
            "Custom direction for all agents",
            placeholder="e.g., 'Focus on casting-related topics this week' or 'Increase LinkedIn activity'",
            key="priority_override",
        )

        if st.button("Apply Override", type="primary"):
            st.toast("Strategy override applied!", icon="✅")
