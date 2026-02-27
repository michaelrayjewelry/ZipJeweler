"""Inline approve/reject/edit content widget."""

import streamlit as st

from zipjeweler.dashboard.db import get_db, update_content_status


def render_approval_queue(contents: list):
    """Render the content approval queue with inline actions."""
    drafts = [c for c in contents if c.status == "draft"]

    if not drafts:
        st.success("No content pending approval. All caught up!")
        return

    st.markdown(f"**{len(drafts)}** items pending approval")

    for content in drafts:
        with st.container(border=True):
            # Header
            type_label = content.content_type.replace("_", " ").title()
            st.markdown(f"### {type_label} for {content.target_platform}")

            # Content preview
            text = content.final_text or content.text_draft or ""
            st.text_area(
                "Content",
                value=text,
                height=120,
                key=f"preview_{content.id}",
                disabled=True,
            )

            if content.image_url:
                st.caption(f"Image: {content.image_url}")
            if content.strategy_notes:
                st.caption(f"Strategy: {content.strategy_notes}")
            if content.ab_variant:
                st.caption(f"A/B Test: Variant {content.ab_variant} (Group: {content.ab_test_group})")

            # Action buttons
            col_approve, col_edit, col_reject = st.columns(3)

            with col_approve:
                if st.button(
                    "Approve",
                    key=f"q_approve_{content.id}",
                    type="primary",
                    use_container_width=True,
                ):
                    with get_db() as session:
                        update_content_status(session, content.id, "approved")
                    st.toast(f"Content #{content.id} approved!", icon="check")
                    st.rerun()

            with col_edit:
                edit_key = f"edit_mode_{content.id}"
                if st.button(
                    "Edit",
                    key=f"q_edit_{content.id}",
                    use_container_width=True,
                ):
                    st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                    st.rerun()

            with col_reject:
                if st.button(
                    "Reject",
                    key=f"q_reject_{content.id}",
                    use_container_width=True,
                ):
                    with get_db() as session:
                        update_content_status(session, content.id, "rejected")
                    st.toast(f"Content #{content.id} rejected", icon="x")
                    st.rerun()

            # Inline edit form
            if st.session_state.get(f"edit_mode_{content.id}", False):
                edited_text = st.text_area(
                    "Edit content",
                    value=text,
                    height=150,
                    key=f"edited_{content.id}",
                )
                if st.button(
                    "Save & Approve",
                    key=f"save_approve_{content.id}",
                    type="primary",
                ):
                    with get_db() as session:
                        update_content_status(session, content.id, "approved", edits=edited_text)
                    st.session_state[f"edit_mode_{content.id}"] = False
                    st.toast(f"Content #{content.id} edited and approved!", icon="check")
                    st.rerun()
