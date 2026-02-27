"""Learning model — insights, strategy changes, and retrospective data."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from zipjeweler.models.database import Base


class Learning(Base):
    """Individual insights extracted by the Learning Agent."""

    __tablename__ = "learnings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_validated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Insight
    category: Mapped[str] = mapped_column(String(50))
    # content, timing, platform, audience, topic, reply_style, keyword
    insight: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=50.0)  # 0-100, decays over time
    applied: Mapped[bool] = mapped_column(Boolean, default=False)

    # Human direction
    direction: Mapped[str] = mapped_column(Text, default="")

    # Google Sheets sync
    sheets_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Learning(id={self.id}, category={self.category}, "
            f"confidence={self.confidence})>"
        )


class Intelligence(Base):
    """Daily brief items — opportunities, competitor moves, AI gaps."""

    __tablename__ = "intelligence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Classification
    date: Mapped[str] = mapped_column(String(20))  # YYYY-MM-DD
    type: Mapped[str] = mapped_column(String(50))
    # ai_gap, competitor_move, keyword_opportunity, market_shift
    description: Mapped[str] = mapped_column(Text)
    dollar_value: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[int] = mapped_column(Integer, default=3)  # 1-5
    competitor: Mapped[str] = mapped_column(String(200), default="")
    source: Mapped[str] = mapped_column(String(200), default="")
    draft_content: Mapped[str] = mapped_column(Text, default="")

    # Status
    status: Mapped[str] = mapped_column(String(50), default="new")
    # new, acting_on, captured, dismissed
    direction: Mapped[str] = mapped_column(Text, default="")

    # Google Sheets sync
    sheets_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Intelligence(id={self.id}, type={self.type}, "
            f"priority={self.priority}, $={self.dollar_value})>"
        )


class Retrospective(Base):
    """Weekly/monthly strategy retrospectives."""

    __tablename__ = "retrospectives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    date: Mapped[str] = mapped_column(String(20))
    period: Mapped[str] = mapped_column(String(100))  # "Week of Feb 24" etc.
    type: Mapped[str] = mapped_column(String(20))  # weekly, monthly

    top_performing_content: Mapped[str] = mapped_column(Text, default="")
    top_performing_platform: Mapped[str] = mapped_column(String(50), default="")
    top_performing_segment: Mapped[str] = mapped_column(String(100), default="")
    ab_test_results: Mapped[str] = mapped_column(Text, default="")
    strategy_changes_made: Mapped[str] = mapped_column(Text, default="")
    emerging_trends: Mapped[str] = mapped_column(Text, default="")
    goals_vs_actual: Mapped[str] = mapped_column(Text, default="")
    next_period_goals: Mapped[str] = mapped_column(Text, default="")
    self_improvement_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Human direction
    direction: Mapped[str] = mapped_column(Text, default="")

    # Google Sheets sync
    sheets_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Retrospective(id={self.id}, period={self.period}, type={self.type})>"
