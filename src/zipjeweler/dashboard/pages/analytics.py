"""Page 6: Analytics — Engagement charts, lead funnel, sentiment, ROI."""

import streamlit as st

from zipjeweler.dashboard.db import (
    get_db,
    get_engagement_over_time,
    get_leads_by_nurture_stage,
    get_leads_by_platform,
    get_recent_engagements,
    get_recent_leads,
    get_total_engagement,
)
from zipjeweler.dashboard.components.charts import (
    render_engagement_timeline,
    render_funnel_chart,
    render_platform_pie,
    render_score_distribution,
)


def page():
    st.title("Analytics — Performance & Insights")
    st.caption("Deep dive into engagement data, lead funnels, sentiment, and ROI.")
    st.markdown("---")

    with get_db() as session:
        total_eng = get_total_engagement(session)
        timeline_data = get_engagement_over_time(session, days=30)
        funnel_data = get_leads_by_nurture_stage(session)
        platform_data = get_leads_by_platform(session)
        leads = get_recent_leads(session, limit=200)
        engagements = get_recent_engagements(session, limit=200)

    # --- Top KPIs ---
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Likes", f"{total_eng['likes']:,}")
    with col2:
        st.metric("Total Shares", f"{total_eng['shares']:,}")
    with col3:
        st.metric("Total Comments", f"{total_eng['comments']:,}")
    with col4:
        st.metric("Total Clicks", f"{total_eng['clicks']:,}")
    with col5:
        st.metric("Total Impressions", f"{total_eng['impressions']:,}")

    st.markdown("---")

    # --- Tabs ---
    tab_engagement, tab_funnel, tab_platform, tab_sentiment, tab_roi = st.tabs([
        "Engagement", "Lead Funnel", "Platform Comparison", "Sentiment", "ROI Calculator",
    ])

    # --- Engagement Tab ---
    with tab_engagement:
        st.subheader("Engagement Over Time")
        days = st.selectbox("Period", [7, 14, 30, 60, 90], index=2, key="eng_days")
        with get_db() as session:
            data = get_engagement_over_time(session, days=days)
        render_engagement_timeline(data, f"Engagement — Last {days} Days")

        # Top posts
        st.subheader("Top Performing Posts")
        sorted_eng = sorted(engagements, key=lambda e: e.likes + e.shares + e.clicks, reverse=True)
        for eng in sorted_eng[:5]:
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.markdown(f"**{eng.platform}** — {eng.post_type}")
                with col2:
                    st.metric("Likes", eng.likes)
                with col3:
                    st.metric("Shares", eng.shares)
                with col4:
                    st.metric("Comments", eng.comments)
                with col5:
                    st.metric("Clicks", eng.clicks)

    # --- Funnel Tab ---
    with tab_funnel:
        st.subheader("Lead Nurture Funnel")
        render_funnel_chart(funnel_data)

        # Drop-off analysis
        st.subheader("Drop-off Analysis")
        stages = funnel_data
        for i in range(len(stages) - 1):
            current = stages[i]["count"]
            next_stage = stages[i + 1]["count"]
            if current > 0:
                retention = (next_stage / current) * 100
                loss = 100 - retention
                st.caption(
                    f"{stages[i]['stage'].replace('_', ' ').title()} → "
                    f"{stages[i + 1]['stage'].replace('_', ' ').title()}: "
                    f"**{retention:.0f}%** retained, **{loss:.0f}%** dropped"
                )

    # --- Platform Comparison ---
    with tab_platform:
        st.subheader("Platform Comparison")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            render_platform_pie(platform_data, "Leads by Platform")
        with col_p2:
            render_score_distribution(leads, "Lead Score Distribution")

        # Per-platform breakdown
        st.subheader("Per-Platform Metrics")
        platform_names = set(e.platform for e in engagements) if engagements else set()
        for plat in sorted(platform_names):
            plat_engs = [e for e in engagements if e.platform == plat]
            with st.expander(f"**{plat.title()}** ({len(plat_engs)} posts)"):
                total_likes = sum(e.likes for e in plat_engs)
                total_shares = sum(e.shares for e in plat_engs)
                total_clicks = sum(e.clicks for e in plat_engs)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Likes", total_likes)
                with col2:
                    st.metric("Shares", total_shares)
                with col3:
                    st.metric("Clicks", total_clicks)

    # --- Sentiment Tab ---
    with tab_sentiment:
        st.subheader("Sentiment Analysis")

        total_pos = sum(e.positive_responses for e in engagements)
        total_neg = sum(e.negative_responses for e in engagements)
        total_q = sum(e.question_responses for e in engagements)
        total_resp = total_pos + total_neg + total_q

        if total_resp > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Positive", total_pos)
            with col2:
                st.metric("Negative", total_neg)
            with col3:
                st.metric("Questions", total_q)
            with col4:
                pos_pct = (total_pos / total_resp) * 100
                st.metric("Positive Rate", f"{pos_pct:.0f}%")

            import plotly.express as px

            sentiment_data = [
                {"Sentiment": "Positive", "Count": total_pos},
                {"Sentiment": "Negative", "Count": total_neg},
                {"Sentiment": "Questions", "Count": total_q},
            ]
            fig = px.pie(
                sentiment_data,
                names="Sentiment",
                values="Count",
                title="Response Sentiment Breakdown",
                color="Sentiment",
                color_discrete_map={"Positive": "#2E7D32", "Negative": "#C62828", "Questions": "#1565C0"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sentiment data yet. Publish content and track responses to see sentiment analysis.")

    # --- ROI Tab ---
    with tab_roi:
        st.subheader("ROI Calculator")
        st.caption("Estimate the return on investment from your social media agents.")

        col1, col2 = st.columns(2)
        with col1:
            clv = st.number_input("Customer Lifetime Value ($)", 100, 100000, 5000, step=500, key="clv")
            conv_rate = st.slider("Lead-to-Customer Conversion Rate (%)", 0.1, 20.0, 2.0, 0.1, key="conv_rate")
            monthly_api_cost = st.number_input("Monthly API Cost ($)", 0, 10000, 200, step=50, key="api_cost")

        with col2:
            total_leads = len(leads)
            qualified = len([l for l in leads if l.lead_score >= 70])
            est_customers = qualified * (conv_rate / 100)
            est_revenue = est_customers * clv
            roi = ((est_revenue - monthly_api_cost) / monthly_api_cost * 100) if monthly_api_cost > 0 else 0

            st.metric("Total Leads Discovered", total_leads)
            st.metric("Qualified Leads (Score >= 70)", qualified)
            st.metric("Est. Customers", f"{est_customers:.1f}")
            st.metric("Est. Revenue", f"${est_revenue:,.0f}")
            st.metric("Est. Monthly ROI", f"{roi:,.0f}%")
