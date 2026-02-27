"""Database helpers for the Streamlit dashboard."""

from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import Session, sessionmaker

# Direct imports to avoid circular dependency with settings
# db.py is at src/zipjeweler/dashboard/db.py → parents[3] = project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "db" / "zipjeweler.db"


def _get_engine():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{DB_PATH}", echo=False)


def _get_session_factory():
    return sessionmaker(bind=_get_engine())


@contextmanager
def get_db():
    """Context manager for database sessions."""
    session = _get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ensure_tables():
    """Create all tables if they don't exist."""
    from zipjeweler.models.database import Base
    from zipjeweler.models.content import Content  # noqa: F401
    from zipjeweler.models.engagement import Engagement  # noqa: F401
    from zipjeweler.models.lead import Lead  # noqa: F401
    from zipjeweler.models.learning import Intelligence, Learning, Retrospective  # noqa: F401

    engine = _get_engine()
    Base.metadata.create_all(bind=engine)


# ---------- Query helpers ----------

def count_leads_today(session: Session) -> int:
    from zipjeweler.models.lead import Lead
    today = datetime.utcnow().date()
    return (
        session.query(func.count(Lead.id))
        .filter(func.date(Lead.created_at) == today)
        .scalar()
        or 0
    )


def count_leads_yesterday(session: Session) -> int:
    from zipjeweler.models.lead import Lead
    yesterday = (datetime.utcnow() - timedelta(days=1)).date()
    return (
        session.query(func.count(Lead.id))
        .filter(func.date(Lead.created_at) == yesterday)
        .scalar()
        or 0
    )


def count_replies_drafted(session: Session) -> int:
    from zipjeweler.models.content import Content
    return (
        session.query(func.count(Content.id))
        .filter(Content.content_type == "reply", Content.status == "draft")
        .scalar()
        or 0
    )


def count_content_created_today(session: Session) -> int:
    from zipjeweler.models.content import Content
    today = datetime.utcnow().date()
    return (
        session.query(func.count(Content.id))
        .filter(func.date(Content.created_at) == today)
        .scalar()
        or 0
    )


def count_posts_published_today(session: Session) -> int:
    from zipjeweler.models.engagement import Engagement
    today = datetime.utcnow().date()
    return (
        session.query(func.count(Engagement.id))
        .filter(
            func.date(Engagement.created_at) == today,
            Engagement.status == "published",
        )
        .scalar()
        or 0
    )


def get_total_engagement(session: Session) -> dict:
    from zipjeweler.models.engagement import Engagement
    row = (
        session.query(
            func.sum(Engagement.likes).label("likes"),
            func.sum(Engagement.shares).label("shares"),
            func.sum(Engagement.comments).label("comments"),
            func.sum(Engagement.clicks).label("clicks"),
            func.sum(Engagement.impressions).label("impressions"),
        )
        .first()
    )
    return {
        "likes": row.likes or 0,
        "shares": row.shares or 0,
        "comments": row.comments or 0,
        "clicks": row.clicks or 0,
        "impressions": row.impressions or 0,
    }


def get_leads_by_platform(session: Session) -> list[dict]:
    from zipjeweler.models.lead import Lead
    rows = (
        session.query(Lead.platform, func.count(Lead.id).label("count"))
        .group_by(Lead.platform)
        .all()
    )
    return [{"platform": r.platform, "count": r.count} for r in rows]


def get_leads_by_status(session: Session) -> list[dict]:
    from zipjeweler.models.lead import Lead
    rows = (
        session.query(Lead.status, func.count(Lead.id).label("count"))
        .group_by(Lead.status)
        .all()
    )
    return [{"status": r.status, "count": r.count} for r in rows]


def get_leads_by_topic(session: Session) -> list[dict]:
    from zipjeweler.models.lead import Lead
    rows = (
        session.query(Lead.topic_category, func.count(Lead.id).label("count"))
        .group_by(Lead.topic_category)
        .all()
    )
    return [{"topic": r.topic_category, "count": r.count} for r in rows]


def get_leads_by_nurture_stage(session: Session) -> list[dict]:
    from zipjeweler.models.lead import Lead
    stages = ["discovery", "first_touch", "follow_up", "soft_pitch", "conversion", "post_conversion"]
    rows = (
        session.query(Lead.nurture_stage, func.count(Lead.id).label("count"))
        .group_by(Lead.nurture_stage)
        .all()
    )
    stage_counts = {r.nurture_stage: r.count for r in rows}
    return [{"stage": s, "count": stage_counts.get(s, 0)} for s in stages]


def get_content_by_status(session: Session) -> list[dict]:
    from zipjeweler.models.content import Content
    rows = (
        session.query(Content.status, func.count(Content.id).label("count"))
        .group_by(Content.status)
        .all()
    )
    return [{"status": r.status, "count": r.count} for r in rows]


def get_content_by_platform(session: Session) -> list[dict]:
    from zipjeweler.models.content import Content
    rows = (
        session.query(Content.target_platform, func.count(Content.id).label("count"))
        .group_by(Content.target_platform)
        .all()
    )
    return [{"platform": r.target_platform, "count": r.count} for r in rows]


def get_engagement_over_time(session: Session, days: int = 30) -> list[dict]:
    from zipjeweler.models.engagement import Engagement
    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = (
        session.query(
            func.date(Engagement.created_at).label("date"),
            func.sum(Engagement.likes).label("likes"),
            func.sum(Engagement.shares).label("shares"),
            func.sum(Engagement.comments).label("comments"),
            func.sum(Engagement.clicks).label("clicks"),
        )
        .filter(Engagement.created_at >= cutoff)
        .group_by(func.date(Engagement.created_at))
        .order_by(func.date(Engagement.created_at))
        .all()
    )
    return [
        {
            "date": r.date,
            "likes": r.likes or 0,
            "shares": r.shares or 0,
            "comments": r.comments or 0,
            "clicks": r.clicks or 0,
        }
        for r in rows
    ]


def get_recent_intelligence(session: Session, limit: int = 20) -> list:
    from zipjeweler.models.learning import Intelligence
    return (
        session.query(Intelligence)
        .order_by(Intelligence.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_leads(session: Session, limit: int = 50) -> list:
    from zipjeweler.models.lead import Lead
    return (
        session.query(Lead)
        .order_by(Lead.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_content(session: Session, limit: int = 50) -> list:
    from zipjeweler.models.content import Content
    return (
        session.query(Content)
        .order_by(Content.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_engagements(session: Session, limit: int = 50) -> list:
    from zipjeweler.models.engagement import Engagement
    return (
        session.query(Engagement)
        .order_by(Engagement.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_learnings(session: Session, limit: int = 50) -> list:
    from zipjeweler.models.learning import Learning
    return (
        session.query(Learning)
        .order_by(Learning.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_retrospectives(session: Session, limit: int = 10) -> list:
    from zipjeweler.models.learning import Retrospective
    return (
        session.query(Retrospective)
        .order_by(Retrospective.created_at.desc())
        .limit(limit)
        .all()
    )


def update_content_status(session: Session, content_id: int, status: str, edits: str = ""):
    from zipjeweler.models.content import Content
    content = session.query(Content).get(content_id)
    if content:
        content.status = status
        if edits:
            content.human_edits = edits
        content.updated_at = datetime.utcnow()


def update_lead_status(session: Session, lead_id: int, status: str, notes: str = ""):
    from zipjeweler.models.lead import Lead
    lead = session.query(Lead).get(lead_id)
    if lead:
        lead.status = status
        if notes:
            lead.notes = notes
        lead.updated_at = datetime.utcnow()


def update_intelligence_status(session: Session, intel_id: int, status: str, direction: str = ""):
    from zipjeweler.models.learning import Intelligence
    item = session.query(Intelligence).get(intel_id)
    if item:
        item.status = status
        if direction:
            item.direction = direction
