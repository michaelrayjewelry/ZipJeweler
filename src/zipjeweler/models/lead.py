"""Lead model — discovered prospects from social listening."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from zipjeweler.models.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Source
    platform: Mapped[str] = mapped_column(String(50))  # reddit, twitter, linkedin, etc.
    source_url: Mapped[str] = mapped_column(String(500))
    author: Mapped[str] = mapped_column(String(200))
    content_snippet: Mapped[str] = mapped_column(Text)

    # Classification
    topic_category: Mapped[str] = mapped_column(String(100))  # cad_modelers, casting_issues, etc.
    audience_segment: Mapped[str] = mapped_column(String(100), default="unknown")
    pain_points_detected: Mapped[str] = mapped_column(Text, default="")  # JSON list

    # Scoring
    lead_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    dollar_value: Mapped[float] = mapped_column(Float, default=0.0)
    pain_point_relevance: Mapped[float] = mapped_column(Float, default=0.0)
    purchase_intent: Mapped[float] = mapped_column(Float, default=0.0)
    influence_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Nurture tracking
    nurture_stage: Mapped[str] = mapped_column(String(50), default="discovery")
    # discovery, first_touch, follow_up, soft_pitch, conversion, post_conversion
    last_engagement_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    engagement_count: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="new")
    # new, reply_drafted, replied, contacted, converted, dismissed
    reply_drafted: Mapped[str] = mapped_column(Text, default="")

    # Human direction (from Google Sheets)
    notes: Mapped[str] = mapped_column(Text, default="")

    # Google Sheets sync
    sheets_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Lead(id={self.id}, platform={self.platform}, "
            f"score={self.lead_score}, stage={self.nurture_stage})>"
        )
