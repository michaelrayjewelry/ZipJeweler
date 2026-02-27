"""Global settings loaded from environment variables and .env file."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """All configuration for ZipJeweler agents, loaded from .env."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM Providers ---
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # --- Reddit ---
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "ZipJeweler Social Agent v0.1"
    reddit_username: str = ""
    reddit_password: str = ""

    # --- X / Twitter ---
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    twitter_bearer_token: str = ""

    # --- LinkedIn ---
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    linkedin_access_token: str = ""

    # --- Facebook / Instagram ---
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_page_access_token: str = ""
    meta_page_id: str = ""
    instagram_business_account_id: str = ""

    # --- Pinterest ---
    pinterest_access_token: str = ""
    pinterest_board_id: str = ""

    # --- Google Sheets ---
    google_service_account_file: str = "service_account.json"
    google_spreadsheet_id: str = ""

    # --- Image Generation ---
    stability_api_key: str = ""

    # --- Notifications ---
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    notification_email_to: str = ""

    # --- Agent Behavior ---
    human_approval_required: bool = True
    dry_run: bool = True
    log_level: str = "INFO"

    # --- Database ---
    database_url: str = Field(
        default=f"sqlite:///{PROJECT_ROOT / 'data' / 'db' / 'zipjeweler.db'}"
    )

    # --- LLM Model Selection ---
    primary_model: str = "anthropic/claude-sonnet-4-20250514"
    fast_model: str = "anthropic/claude-haiku-4-5-20251001"
    embedding_model: str = "text-embedding-3-small"

    # --- Paths ---
    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT

    @property
    def config_dir(self) -> Path:
        return PROJECT_ROOT / "config"

    @property
    def data_dir(self) -> Path:
        return PROJECT_ROOT / "data"

    @property
    def knowledge_dir(self) -> Path:
        return PROJECT_ROOT / "data" / "knowledge"


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
