"""Page 4: Content — Content calendar, drafts, A/B tests, brand voice."""

import streamlit as st

from zipjeweler.dashboard.db import (
    get_content_by_platform,
    get_content_by_status,
    get_db,
    get_recent_content,
)
from zipjeweler.dashboard.components.approval_widget import render_approval_queue
from zipjeweler.dashboard.components.charts import render_platform_pie, render_status_bar
from zipjeweler.dashboard.components.data_tables import render_content_table


def page():
    st.title("Content — Creation & Management")
    st.caption("Manage content drafts, A/B tests, and brand voice configuration.")
    st.markdown("---")

    # --- Overview ---
    with get_db() as session:
        status_data = get_content_by_status(session)
        platform_data = get_content_by_platform(session)
        all_content = get_recent_content(session, limit=100)

    col1, col2 = st.columns(2)
    with col1:
        render_status_bar(status_data, "Content by Status")
    with col2:
        render_platform_pie(platform_data, "Content by Platform")

    st.markdown("---")

    # --- Tabs ---
    tab_drafts, tab_approved, tab_ab, tab_generate, tab_brand = st.tabs([
        "Drafts", "All Content", "A/B Tests", "Generate", "Brand Voice",
    ])

    # --- Drafts Tab ---
    with tab_drafts:
        st.subheader("Content Approval Queue")
        drafts = [c for c in all_content if c.content_type != "reply"]
        render_approval_queue(drafts)

    # --- All Content Tab ---
    with tab_approved:
        st.subheader("All Content")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            type_filter = st.selectbox(
                "Content Type",
                ["All", "text", "image", "text_image", "reply"],
                key="content_type_filter",
            )
        with col_f2:
            platform_filter = st.selectbox(
                "Platform",
                ["All", "reddit", "twitter", "linkedin", "facebook", "instagram", "pinterest"],
                key="content_platform_filter",
            )
        with col_f3:
            status_filter = st.selectbox(
                "Status",
                ["All", "draft", "approved", "rejected", "edited", "posted"],
                key="content_status_filter",
            )

        filtered = all_content
        if type_filter != "All":
            filtered = [c for c in filtered if c.content_type == type_filter]
        if platform_filter != "All":
            filtered = [c for c in filtered if c.target_platform == platform_filter]
        if status_filter != "All":
            filtered = [c for c in filtered if c.status == status_filter]

        st.caption(f"Showing {len(filtered)} items")
        render_content_table(filtered)

    # --- A/B Tests Tab ---
    with tab_ab:
        st.subheader("A/B Test Dashboard")
        ab_content = [c for c in all_content if c.ab_test_group]

        if not ab_content:
            st.info("No A/B tests running yet. The Content Crew will create variants automatically.")
        else:
            # Group by test group
            groups: dict[str, list] = {}
            for c in ab_content:
                groups.setdefault(c.ab_test_group, []).append(c)

            for group_id, variants in groups.items():
                with st.expander(f"Test: {group_id} ({len(variants)} variants)"):
                    for v in variants:
                        with st.container(border=True):
                            st.markdown(f"**Variant {v.ab_variant}** — {v.target_platform} — Status: {v.status}")
                            st.text((v.final_text or v.text_draft or "")[:200])

    # --- Generate Tab ---
    with tab_generate:
        st.subheader("On-Demand Content Generation")
        st.caption("Generate content immediately without waiting for the scheduler.")

        gen_platform = st.selectbox(
            "Target Platform",
            ["reddit", "twitter", "linkedin", "facebook", "instagram", "pinterest"],
            key="gen_platform",
        )
        gen_type = st.selectbox(
            "Content Type",
            ["text", "image", "text_image"],
            key="gen_type",
        )
        gen_topic = st.selectbox(
            "Topic Category",
            [
                "cad_modelers", "jewelry_designers", "custom_jewelry_questions",
                "jewelry_production", "casting_issues", "looking_for_cad",
                "looking_for_designers", "looking_for_manufacturers",
                "business_management_pain",
            ],
            key="gen_topic",
        )
        gen_notes = st.text_area("Strategy notes (optional)", key="gen_notes")

        if st.button("Generate Content", type="primary"):
            st.toast(
                f"Generating {gen_type} for {gen_platform} about {gen_topic}...",
                icon="📝",
            )

    # --- Brand Voice Tab ---
    with tab_brand:
        st.subheader("Brand Voice Configuration")

        st.markdown("#### Tone")
        st.text_area(
            "Brand Tone",
            value="Professional but approachable. Knowledgeable about the jewelry industry. Helpful first, promotional second.",
            height=80,
            key="brand_tone",
        )

        st.markdown("#### Do's")
        dos = [
            "Lead with value — answer the question first",
            "Use jewelry industry terminology naturally",
            "Share specific examples of how ZipJeweler solves problems",
            "Be conversational and authentic",
            "Mention ZipJeweler naturally, like recommending to a friend",
        ]
        for d in dos:
            st.checkbox(d, value=True, key=f"do_{d[:20]}")

        st.markdown("#### Don'ts")
        donts = [
            "Sound like a generic ad or spam bot",
            "Use aggressive sales language",
            "Disparage competitors by name",
            "Make unsubstantiated claims",
            "Post the same reply twice",
        ]
        for d in donts:
            st.checkbox(d, value=True, key=f"dont_{d[:20]}")

        st.markdown("#### Hashtags")
        st.text_input(
            "Primary Hashtags",
            value="#ZipJeweler, #JewelryBusiness, #JewelerLife",
            key="primary_hashtags",
        )
        st.text_input(
            "Secondary Hashtags",
            value="#JewelryDesign, #CustomJewelry, #JewelryMaking, #JewelryCRM",
            key="secondary_hashtags",
        )

        if st.button("Save Brand Voice", type="primary"):
            st.toast("Brand voice settings saved!", icon="✅")
