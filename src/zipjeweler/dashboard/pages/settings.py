"""Page 8: Settings — API keys, autonomy levels, schedules, cost controls."""

from pathlib import Path

import streamlit as st
import yaml


def _load_yaml(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


def page():
    st.title("Settings — System Configuration")
    st.caption("Manage API keys, autonomy levels, schedules, notifications, and cost controls.")
    st.markdown("---")

    tab_api, tab_autonomy, tab_schedule, tab_notify, tab_brand, tab_audience, tab_cost = st.tabs([
        "API Keys", "Autonomy", "Schedules", "Notifications",
        "Brand Config", "Target Audience", "Cost Controls",
    ])

    # --- API Keys ---
    with tab_api:
        st.subheader("API Key Management")
        st.caption("API keys are loaded from the .env file. Update values here to test connections.")

        api_sections = {
            "LLM Providers": [
                ("Anthropic API Key", "anthropic_api_key", "password"),
                ("OpenAI API Key", "openai_api_key", "password"),
            ],
            "Reddit (PRAW)": [
                ("Client ID", "reddit_client_id", "default"),
                ("Client Secret", "reddit_client_secret", "password"),
                ("Username", "reddit_username", "default"),
                ("Password", "reddit_password", "password"),
            ],
            "Twitter/X (Tweepy)": [
                ("API Key", "twitter_api_key", "default"),
                ("API Secret", "twitter_api_secret", "password"),
                ("Bearer Token", "twitter_bearer_token", "password"),
            ],
            "LinkedIn": [
                ("Client ID", "linkedin_client_id", "default"),
                ("Client Secret", "linkedin_client_secret", "password"),
                ("Access Token", "linkedin_access_token", "password"),
            ],
            "Meta (Facebook/Instagram)": [
                ("App ID", "meta_app_id", "default"),
                ("App Secret", "meta_app_secret", "password"),
                ("Page Access Token", "meta_page_access_token", "password"),
                ("Page ID", "meta_page_id", "default"),
                ("Instagram Business Account ID", "instagram_business_account_id", "default"),
            ],
            "Pinterest": [
                ("Access Token", "pinterest_access_token", "password"),
                ("Board ID", "pinterest_board_id", "default"),
            ],
            "Google Sheets": [
                ("Service Account File", "google_service_account_file", "default"),
                ("Spreadsheet ID", "google_spreadsheet_id", "default"),
            ],
            "Image Generation": [
                ("Stability AI Key", "stability_api_key", "password"),
            ],
        }

        for section_name, keys in api_sections.items():
            with st.expander(f"**{section_name}**"):
                for label, env_var, input_type in keys:
                    st.text_input(
                        label,
                        value="",
                        type=input_type,
                        key=f"api_{env_var}",
                        placeholder=f"Set {env_var} in .env",
                    )
                if st.button(f"Test {section_name} Connection", key=f"test_{section_name}"):
                    st.toast(f"Testing {section_name} connection...", icon="magnifying_glass")

    # --- Autonomy Levels ---
    with tab_autonomy:
        st.subheader("Autonomy Levels")
        st.caption("Control how much human oversight each crew requires.")

        autonomy_options = ["Full Human Approval", "Auto with Review", "Fully Autonomous"]
        crews = [
            "Intelligence", "Listening", "Engagement",
            "Content", "Posting", "Analytics", "Evolution",
        ]

        for crew in crews:
            st.select_slider(
                f"{crew} Crew",
                options=autonomy_options,
                value="Full Human Approval",
                key=f"autonomy_{crew}",
            )

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.toggle("Dry Run Mode", value=True, key="dry_run_toggle", help="When on, no actual posts are published")
        with col2:
            st.toggle("Human Approval Required", value=True, key="approval_toggle", help="Require approval for all content")

    # --- Schedules ---
    with tab_schedule:
        st.subheader("Crew Run Schedules")

        schedules = {
            "Intelligence": {"type": "daily", "time": "05:00", "desc": "Daily at 05:00 UTC"},
            "Listening": {"type": "interval", "minutes": 60, "desc": "Every 60 minutes"},
            "Engagement": {"type": "interval", "minutes": 120, "desc": "Every 2 hours"},
            "Content Creation": {"type": "interval", "minutes": 240, "desc": "Every 4 hours"},
            "Posting": {"type": "interval", "minutes": 60, "desc": "Every 60 minutes"},
            "Analytics": {"type": "interval", "minutes": 720, "desc": "Every 12 hours"},
            "Evolution": {"type": "daily", "time": "04:00", "desc": "Daily at 04:00 UTC"},
        }

        for crew, sched in schedules.items():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**{crew}**")
                    st.caption(sched["desc"])
                with col2:
                    if sched["type"] == "daily":
                        st.time_input(
                            "Run at (UTC)",
                            value=None,
                            key=f"sched_time_{crew}",
                        )
                    else:
                        st.number_input(
                            "Interval (minutes)",
                            1, 1440,
                            sched["minutes"],
                            key=f"sched_min_{crew}",
                        )
                with col3:
                    st.toggle("Enabled", value=True, key=f"sched_enabled_{crew}")

    # --- Notifications ---
    with tab_notify:
        st.subheader("Notification Settings")

        st.markdown("#### Email Notifications")
        st.text_input("SMTP Host", value="smtp.gmail.com", key="smtp_host")
        st.number_input("SMTP Port", 1, 65535, 587, key="smtp_port")
        st.text_input("SMTP Username", key="smtp_user")
        st.text_input("SMTP Password", type="password", key="smtp_pass")
        st.text_input("Send notifications to", key="notify_email", placeholder="you@example.com")

        st.markdown("#### Notification Triggers")
        triggers = [
            "Daily brief generated",
            "High-score lead discovered (score >= 80)",
            "Content ready for review",
            "All replies approved and posted",
            "Agent error occurred",
            "Weekly retrospective ready",
            "A/B test winner determined",
        ]
        for trigger in triggers:
            st.checkbox(trigger, value=True, key=f"notify_{trigger[:20]}")

    # --- Brand Config ---
    with tab_brand:
        st.subheader("Brand Guidelines (YAML)")
        config_path = Path(__file__).resolve().parents[4] / "config" / "brand_guidelines.yaml"
        brand_yaml = _load_yaml(config_path)

        yaml_text = yaml.dump(brand_yaml, default_flow_style=False, sort_keys=False) if brand_yaml else ""
        edited = st.text_area(
            "brand_guidelines.yaml",
            value=yaml_text,
            height=400,
            key="brand_yaml_editor",
        )

        if st.button("Save Brand Config", type="primary"):
            try:
                yaml.safe_load(edited)
                st.toast("Brand config validated! (Save to file in production mode)", icon="check")
            except yaml.YAMLError as e:
                st.error(f"Invalid YAML: {e}")

    # --- Target Audience ---
    with tab_audience:
        st.subheader("Target Audience (YAML)")
        config_path = Path(__file__).resolve().parents[4] / "config" / "target_audience.yaml"
        audience_yaml = _load_yaml(config_path)

        yaml_text = yaml.dump(audience_yaml, default_flow_style=False, sort_keys=False) if audience_yaml else ""
        edited = st.text_area(
            "target_audience.yaml",
            value=yaml_text,
            height=400,
            key="audience_yaml_editor",
        )

        if st.button("Save Audience Config", type="primary"):
            try:
                yaml.safe_load(edited)
                st.toast("Audience config validated!", icon="check")
            except yaml.YAMLError as e:
                st.error(f"Invalid YAML: {e}")

    # --- Cost Controls ---
    with tab_cost:
        st.subheader("API Cost Controls")

        st.markdown("#### Budget Limits")
        daily_budget = st.number_input("Daily Budget ($)", 0, 1000, 50, step=10, key="daily_budget")
        weekly_budget = st.number_input("Weekly Budget ($)", 0, 5000, 200, step=50, key="weekly_budget")
        monthly_budget = st.number_input("Monthly Budget ($)", 0, 20000, 500, step=100, key="monthly_budget")

        st.markdown("#### Alert Thresholds")
        st.slider(
            "Alert when daily spend exceeds (%)",
            10, 100, 80, key="daily_alert_pct",
            help="Send notification when this percentage of daily budget is consumed",
        )

        st.markdown("#### Estimated Costs")
        cost_data = {
            "Claude Sonnet (content)": "$0.003/1K tokens",
            "Claude Haiku (classification)": "$0.00025/1K tokens",
            "Stability AI (images)": "$0.002-0.006/image",
            "Reddit API": "Free < 100 req/min",
            "Twitter API": "Free tier: 1,500 tweets/month",
            "Google Sheets API": "Free < 500 req/100sec",
        }
        for service, cost in cost_data.items():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.text(service)
            with col2:
                st.caption(cost)
