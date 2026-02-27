"""Tests for SQLAlchemy models."""

from datetime import datetime

from zipjeweler.models.content import Content
from zipjeweler.models.engagement import Engagement
from zipjeweler.models.lead import Lead
from zipjeweler.models.learning import Intelligence, Learning, Retrospective


def test_create_lead(db_session):
    lead = Lead(
        platform="reddit",
        source_url="https://reddit.com/r/jewelers/test",
        author="test_user",
        content_snippet="I need help with inventory tracking",
        topic_category="business_management_pain",
        lead_score=85,
        dollar_value=120.0,
    )
    db_session.add(lead)
    db_session.commit()

    result = db_session.query(Lead).first()
    assert result is not None
    assert result.platform == "reddit"
    assert result.lead_score == 85
    assert result.nurture_stage == "discovery"
    assert result.status == "new"


def test_create_content(db_session):
    content = Content(
        target_platform="reddit",
        content_type="reply",
        text_draft="Have you heard of ZipJeweler? It might help with that.",
        based_on_lead_id=1,
        ab_variant="A",
        ab_test_group="test_001",
    )
    db_session.add(content)
    db_session.commit()

    result = db_session.query(Content).first()
    assert result is not None
    assert result.content_type == "reply"
    assert result.status == "draft"
    assert result.final_text == "Have you heard of ZipJeweler? It might help with that."


def test_content_final_text_uses_edits(db_session):
    content = Content(
        target_platform="twitter",
        content_type="text",
        text_draft="Original draft",
        human_edits="Edited version by human",
    )
    db_session.add(content)
    db_session.commit()

    result = db_session.query(Content).first()
    assert result.final_text == "Edited version by human"


def test_create_engagement(db_session):
    engagement = Engagement(
        content_id=1,
        platform="reddit",
        post_url="https://reddit.com/r/jewelers/test/comment",
        post_type="reply",
        likes=15,
        comments=3,
    )
    db_session.add(engagement)
    db_session.commit()

    result = db_session.query(Engagement).first()
    assert result is not None
    assert result.likes == 15
    assert result.status == "published"


def test_create_learning(db_session):
    learning = Learning(
        category="reply_style",
        insight="Story-based replies get 2.8x more engagement on Reddit",
        evidence="5 posts tested, avg 2.8x improvement",
        confidence=78.5,
    )
    db_session.add(learning)
    db_session.commit()

    result = db_session.query(Learning).first()
    assert result is not None
    assert result.confidence == 78.5
    assert result.applied is False


def test_create_intelligence(db_session):
    intel = Intelligence(
        date="2026-02-27",
        type="ai_gap",
        description="ZipJeweler not mentioned in ChatGPT for 'best jewelry CRM'",
        dollar_value=500.0,
        priority=1,
    )
    db_session.add(intel)
    db_session.commit()

    result = db_session.query(Intelligence).first()
    assert result is not None
    assert result.type == "ai_gap"
    assert result.priority == 1


def test_create_retrospective(db_session):
    retro = Retrospective(
        date="2026-02-27",
        period="Week of Feb 24",
        type="weekly",
        top_performing_platform="reddit",
        self_improvement_score=12.5,
    )
    db_session.add(retro)
    db_session.commit()

    result = db_session.query(Retrospective).first()
    assert result is not None
    assert result.type == "weekly"
    assert result.self_improvement_score == 12.5
