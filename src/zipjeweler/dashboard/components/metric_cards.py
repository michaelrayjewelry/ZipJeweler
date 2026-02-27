"""KPI metric display cards with delta indicators."""

import streamlit as st


def render_metric_row(metrics: list[dict]):
    """Render a row of metric cards.

    Each metric dict: {"label": str, "value": int|str, "delta": int|str|None, "help": str|None}
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            kwargs = {"label": m["label"], "value": m["value"]}
            if m.get("delta") is not None:
                kwargs["delta"] = m["delta"]
            if m.get("help"):
                kwargs["help"] = m["help"]
            st.metric(**kwargs)


def render_kpi_cards(
    leads_today: int,
    leads_delta: int | None,
    replies_drafted: int,
    content_created: int,
    posts_published: int,
    total_engagement: dict | None = None,
):
    """Render the main KPI row for the home page."""
    row1 = [
        {
            "label": "Leads Found Today",
            "value": leads_today,
            "delta": f"{leads_delta:+d} vs yesterday" if leads_delta is not None else None,
            "help": "Leads discovered by listening agents",
        },
        {
            "label": "Replies Drafted",
            "value": replies_drafted,
            "delta": None,
            "help": "Replies pending approval",
        },
        {
            "label": "Content Created",
            "value": content_created,
            "delta": None,
            "help": "Content pieces generated today",
        },
        {
            "label": "Posts Published",
            "value": posts_published,
            "delta": None,
            "help": "Posts published today across platforms",
        },
    ]
    render_metric_row(row1)

    if total_engagement:
        row2 = [
            {"label": "Total Likes", "value": f"{total_engagement['likes']:,}", "delta": None, "help": None},
            {"label": "Total Shares", "value": f"{total_engagement['shares']:,}", "delta": None, "help": None},
            {"label": "Total Comments", "value": f"{total_engagement['comments']:,}", "delta": None, "help": None},
            {"label": "Total Clicks", "value": f"{total_engagement['clicks']:,}", "delta": None, "help": None},
        ]
        render_metric_row(row2)
