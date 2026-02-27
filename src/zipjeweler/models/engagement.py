"""Engagement model — tracks performance of published posts and replies."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from zipjeweler.models.database import Base


class Engagement(Base):
    __tablename__ = "engagements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # What was posted
    content_id: Mapped[int] = mapped_column(Integer)  # FK to content table
    platform: Mapped[str] = mapped_column(String(50))
    post_url: Mapped[str] = mapped_column(String(500), default="")
    post_type: Mapped[str] = mapped_column(String(50))  # organic, reply, comment

    # Metrics (updated by analytics crew)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Sentiment of responses
    positive_responses: Mapped[int] = mapped_column(Integer, default=0)
    negative_responses: Mapped[int] = mapped_column(Integer, default=0)
    question_responses: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_summary: Mapped[str] = mapped_column(Text, default="")

    # A/B test tracking
    ab_variant: Mapped[str] = mapped_column(String(10), default="")
    ab_test_group: Mapped[str] = mapped_column(String(100), default="")

    # Status
    status: Mapped[str] = mapped_column(String(50), default="published")
    # published, scheduled, failed

    # Google Sheets sync
    sheets_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Engagement(id={self.id}, platform={self.platform}, "
            f"likes={self.likes}, engagement_rate={self.engagement_rate})>"
        )
