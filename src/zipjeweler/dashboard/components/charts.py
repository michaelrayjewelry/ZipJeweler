"""Plotly chart helpers for the dashboard."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BRAND_COLORS = ["#1B365D", "#C9A96E", "#4A90D9", "#D4A574", "#2E5090", "#E8C88A", "#333333"]


def render_platform_pie(data: list[dict], title: str = "Leads by Platform"):
    """Pie chart for platform distribution."""
    if not data:
        st.caption("No data available")
        return
    fig = px.pie(
        data,
        names="platform",
        values="count",
        title=title,
        color_discrete_sequence=BRAND_COLORS,
    )
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_status_bar(data: list[dict], title: str = "Items by Status", key_field: str = "status"):
    """Horizontal bar chart for status distribution."""
    if not data:
        st.caption("No data available")
        return
    fig = px.bar(
        data,
        x="count",
        y=key_field,
        orientation="h",
        title=title,
        color=key_field,
        color_discrete_sequence=BRAND_COLORS,
    )
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_topic_bar(data: list[dict], title: str = "Leads by Topic"):
    """Bar chart for topic category distribution."""
    if not data:
        st.caption("No data available")
        return
    fig = px.bar(
        data,
        x="topic",
        y="count",
        title=title,
        color="count",
        color_continuous_scale=["#C9A96E", "#1B365D"],
    )
    fig.update_layout(margin=dict(t=40, b=20, l=0, r=0), height=350)
    st.plotly_chart(fig, use_container_width=True)


def render_funnel_chart(data: list[dict], title: str = "Lead Nurture Funnel"):
    """Funnel chart for lead nurture stages."""
    if not data or all(d["count"] == 0 for d in data):
        st.caption("No funnel data available yet")
        return
    fig = go.Figure(go.Funnel(
        y=[d["stage"].replace("_", " ").title() for d in data],
        x=[d["count"] for d in data],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=BRAND_COLORS[:len(data)]),
    ))
    fig.update_layout(title=title, margin=dict(t=40, b=0, l=0, r=0), height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_engagement_timeline(data: list[dict], title: str = "Engagement Over Time"):
    """Line chart for engagement metrics over time."""
    if not data:
        st.caption("No engagement data available yet")
        return
    fig = go.Figure()
    for metric, color in [("likes", "#1B365D"), ("shares", "#C9A96E"), ("comments", "#4A90D9"), ("clicks", "#D4A574")]:
        fig.add_trace(go.Scatter(
            x=[d["date"] for d in data],
            y=[d[metric] for d in data],
            mode="lines+markers",
            name=metric.title(),
            line=dict(color=color, width=2),
        ))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Count",
        margin=dict(t=40, b=40, l=40, r=0),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_score_distribution(leads: list, title: str = "Lead Score Distribution"):
    """Histogram of lead scores."""
    if not leads:
        st.caption("No lead data available")
        return
    scores = [lead.lead_score for lead in leads]
    fig = px.histogram(
        x=scores,
        nbins=20,
        title=title,
        labels={"x": "Lead Score", "y": "Count"},
        color_discrete_sequence=["#1B365D"],
    )
    fig.update_layout(margin=dict(t=40, b=40, l=40, r=0), height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_gauge(learnings: list, title: str = "Avg Insight Confidence"):
    """Gauge chart showing average learning confidence."""
    if not learnings:
        st.caption("No insights available")
        return
    avg_conf = sum(l.confidence for l in learnings) / len(learnings)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_conf,
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1B365D"},
            "steps": [
                {"range": [0, 40], "color": "#FFE0E0"},
                {"range": [40, 70], "color": "#FFF3E0"},
                {"range": [70, 100], "color": "#E0F2E0"},
            ],
        },
    ))
    fig.update_layout(margin=dict(t=60, b=0, l=20, r=20), height=250)
    st.plotly_chart(fig, use_container_width=True)
