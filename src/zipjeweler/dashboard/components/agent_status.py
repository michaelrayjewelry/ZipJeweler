"""Agent and crew status indicators."""

import streamlit as st

CREW_INFO = [
    {
        "name": "Intelligence",
        "icon": "brain",
        "description": "Generates daily briefs, monitors competitors, tracks AI answers",
        "agents": ["AI Answer Monitor", "Competitor Watcher", "Opportunity Scorer", "Brief Generator"],
        "schedule": "Daily at 05:00 UTC",
    },
    {
        "name": "Listening",
        "icon": "ear",
        "description": "Discovers leads across 6 social platforms",
        "agents": [
            "Reddit Listener", "Twitter Listener", "LinkedIn Listener",
            "Facebook Listener", "Instagram Listener", "Pinterest Listener",
            "Lead Qualifier",
        ],
        "schedule": "Every 60 minutes",
    },
    {
        "name": "Engagement",
        "icon": "speech_balloon",
        "description": "Crafts and posts replies to leads",
        "agents": [
            "Reply Crafter", "Reddit Replier", "Twitter Replier",
            "LinkedIn Replier", "Facebook Replier", "Instagram Replier",
            "Pinterest Replier",
        ],
        "schedule": "Every 120 minutes",
    },
    {
        "name": "Content",
        "icon": "memo",
        "description": "Creates text and image content",
        "agents": ["Content Strategist", "Text Creator", "Image Creator"],
        "schedule": "Every 240 minutes",
    },
    {
        "name": "Posting",
        "icon": "outbox_tray",
        "description": "Publishes approved content across platforms",
        "agents": [
            "Reddit Poster", "Twitter Poster", "LinkedIn Poster",
            "Instagram Poster", "Facebook Poster", "Pinterest Poster",
        ],
        "schedule": "Every 60 minutes",
    },
    {
        "name": "Analytics",
        "icon": "bar_chart",
        "description": "Tracks engagement and extracts insights",
        "agents": ["Engagement Analyst", "Sentiment Analyzer", "Learning Agent"],
        "schedule": "Every 720 minutes",
    },
    {
        "name": "Evolution",
        "icon": "dna",
        "description": "Evolves strategies based on performance data",
        "agents": [
            "A/B Test Manager", "Strategy Evolver", "Lead Nurturer",
            "Content Repurposer", "Trend Detector", "Audience Segmenter",
            "Retrospective Agent",
        ],
        "schedule": "Daily at 04:00 UTC",
    },
]


def _get_crew_status() -> dict[str, str]:
    """Get crew statuses from session state."""
    if "crew_statuses" not in st.session_state:
        st.session_state.crew_statuses = {c["name"]: "idle" for c in CREW_INFO}
    return st.session_state.crew_statuses


def render_crew_status_panel():
    """Render crew status cards with expandable agent details."""
    statuses = _get_crew_status()

    for crew in CREW_INFO:
        name = crew["name"]
        status = statuses.get(name, "idle")
        status_color = {"idle": "gray", "running": "green", "error": "red"}.get(status, "gray")
        status_icon = {"idle": ":material/pause_circle:", "running": ":material/play_circle:", "error": ":material/error:"}.get(status, ":material/pause_circle:")

        with st.expander(f"**{name} Crew** — {crew['description']}", expanded=False):
            col_status, col_schedule, col_action = st.columns([2, 2, 1])

            with col_status:
                if status == "running":
                    st.success(f"Running", icon=":material/play_circle:")
                elif status == "error":
                    st.error(f"Error", icon=":material/error:")
                else:
                    st.info(f"Idle", icon=":material/pause_circle:")

            with col_schedule:
                st.caption(f"Schedule: {crew['schedule']}")

            with col_action:
                if st.button(f"Run", key=f"run_{name}", use_container_width=True):
                    st.session_state.crew_statuses[name] = "running"
                    st.toast(f"{name} Crew started!", icon="rocket")
                    st.rerun()

            st.caption(f"**Agents** ({len(crew['agents'])}): {', '.join(crew['agents'])}")
