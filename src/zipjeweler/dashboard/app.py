"""ZipJeweler Agent Management Dashboard — Main entry point."""

import streamlit as st

st.set_page_config(
    page_title="ZipJeweler Agents",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.title("💎 ZipJeweler Agent Management")
    st.markdown("---")

    # System Overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Leads Found Today", "—", help="Leads discovered by listening agents")
    with col2:
        st.metric("Replies Drafted", "—", help="Replies pending approval")
    with col3:
        st.metric("Content Created", "—", help="Content pieces generated")
    with col4:
        st.metric("Posts Published", "—", help="Posts published across platforms")

    st.markdown("---")

    # Crew Status
    st.subheader("Crew Status")
    crews = [
        ("Intelligence", "Generates daily briefs and monitors competitors"),
        ("Listening", "Discovers leads across 6 social platforms"),
        ("Engagement", "Crafts and posts replies to leads"),
        ("Content", "Creates text and image content"),
        ("Posting", "Publishes approved content"),
        ("Analytics", "Tracks engagement and extracts insights"),
        ("Evolution", "Evolves strategies based on performance"),
    ]

    for crew_name, description in crews:
        with st.expander(f"**{crew_name} Crew** — {description}"):
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.caption(description)
            with col_b:
                st.badge("Idle", icon="⏸️")
            with col_c:
                st.button(f"Run {crew_name}", key=f"run_{crew_name.lower()}")

    st.markdown("---")

    # Quick Actions
    st.subheader("Quick Actions")
    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        st.button("🚀 Run Full Pipeline", type="primary", use_container_width=True)
    with col_q2:
        st.button("📊 Generate Daily Brief", use_container_width=True)
    with col_q3:
        st.button("⏹️ Pause All Agents", use_container_width=True)

    st.markdown("---")
    st.caption("ZipJeweler Social Media Agents v0.1 • Dashboard will expand in Phase 6")


if __name__ == "__main__":
    main()
