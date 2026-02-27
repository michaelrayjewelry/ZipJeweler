"""Content model — generated text, images, and replies."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from zipjeweler.models.database import Base


class Content(Base):
    __tablename__ = "content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Target
    target_platform: Mapped[str] = mapped_column(String(50))
    content_type: Mapped[str] = mapped_column(String(50))  # text, image, text_image, reply

    # Content
    text_draft: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(500), default="")
    image_prompt: Mapped[str] = mapped_column(Text, default="")  # Prompt used to generate image

    # Context
    based_on_lead_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    strategy_notes: Mapped[str] = mapped_column(Text, default="")
    topic_category: Mapped[str] = mapped_column(String(100), default="")

    # A/B Testing
    ab_variant: Mapped[str] = mapped_column(String(10), default="")  # A, B, C, or empty
    ab_test_group: Mapped[str] = mapped_column(String(100), default="")  # Groups variants together

    # Approval
    status: Mapped[str] = mapped_column(String(50), default="draft")
    # draft, approved, rejected, edited, posted
    human_edits: Mapped[str] = mapped_column(Text, default="")
    direction: Mapped[str] = mapped_column(Text, default="")

    # Google Sheets sync
    sheets_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Content(id={self.id}, platform={self.target_platform}, "
            f"type={self.content_type}, status={self.status})>"
        )

    @property
    def final_text(self) -> str:
        """Return human edits if available, otherwise the draft."""
        return self.human_edits if self.human_edits else self.text_draft
