"""CrewAI tool for scoring social-media leads."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any

import structlog
import yaml
from crewai.tools import BaseTool

from zipjeweler.config.settings import get_settings

logger = structlog.get_logger(__name__)


def _load_lead_scoring_config() -> dict:
    """Load the ``lead_scoring`` section from target_audience.yaml."""
    settings = get_settings()
    config_path = settings.config_dir / "target_audience.yaml"
    try:
        with open(config_path) as fh:
            data = yaml.safe_load(fh) or {}
        return data.get("lead_scoring", {})
    except FileNotFoundError:
        logger.warning("lead_scoring_config_not_found", path=str(config_path))
        return {}


def _load_listening_keywords() -> list[str]:
    """Return a flat list of every keyword across all listening topics."""
    settings = get_settings()
    config_path = settings.config_dir / "target_audience.yaml"
    try:
        with open(config_path) as fh:
            data = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        return []
    keywords: list[str] = []
    for topic in data.get("listening_topics", {}).values():
        keywords.extend(topic.get("keywords", []))
    return keywords


def _load_pain_points() -> list[str]:
    """Return a flat list of every pain point across all audience segments."""
    settings = get_settings()
    config_path = settings.config_dir / "target_audience.yaml"
    try:
        with open(config_path) as fh:
            data = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        return []
    pain_points: list[str] = []
    for segment in data.get("audience_segments", {}).values():
        pain_points.extend(segment.get("pain_points", []))
    return pain_points


# ===================================================================
# Individual scoring functions
# ===================================================================

def _score_pain_point_relevance(content: str, pain_points: list[str], keywords: list[str]) -> float:
    """Score 0-100 based on how many pain-point phrases and keywords appear.

    - Each pain-point match is worth more than a keyword match.
    - The score is capped at 100.
    """
    content_lower = content.lower()

    pain_hits = sum(1 for pp in pain_points if pp.lower() in content_lower)
    keyword_hits = sum(1 for kw in keywords if kw.lower() in content_lower)

    # Pain-point matches are weighted more heavily
    raw = (pain_hits * 15) + (keyword_hits * 5)
    return min(raw, 100.0)


def _score_purchase_intent(content: str) -> float:
    """Score 0-100 based on purchase-intent signals in the text.

    Higher scores for explicit buying language, lower for informational.
    """
    content_lower = content.lower()

    high_intent_phrases = [
        "looking for software",
        "need a tool",
        "anyone recommend",
        "recommendation for",
        "best software",
        "what do you use",
        "ready to buy",
        "want to purchase",
        "looking to invest",
        "budget for",
        "price of",
        "how much does",
        "free trial",
        "demo",
        "sign up",
        "need help managing",
        "tired of",
        "frustrated with",
        "switching from",
        "alternative to",
        "compared to",
        "vs ",
        "looking for a solution",
        "need something to",
    ]

    medium_intent_phrases = [
        "how do you manage",
        "how do you track",
        "what tools",
        "any suggestions",
        "help with",
        "struggling with",
        "workflow",
        "automation",
        "streamline",
        "organize",
        "better way to",
    ]

    low_intent_phrases = [
        "just curious",
        "learning about",
        "started making jewelry",
        "new to",
        "beginner",
        "hobby",
    ]

    score = 0.0

    high_hits = sum(1 for p in high_intent_phrases if p in content_lower)
    medium_hits = sum(1 for p in medium_intent_phrases if p in content_lower)
    low_hits = sum(1 for p in low_intent_phrases if p in content_lower)

    score += high_hits * 20
    score += medium_hits * 10
    # Low-intent signals reduce the score slightly
    score -= low_hits * 5

    return max(0.0, min(score, 100.0))


def _score_influence(engagement: dict) -> float:
    """Score 0-100 based on engagement metrics (reach/influence proxy).

    Uses score, num_comments, and upvote_ratio when available.
    """
    post_score = engagement.get("score", 0)
    num_comments = engagement.get("num_comments", 0)
    upvote_ratio = engagement.get("upvote_ratio", 0.5)

    # Logarithmic scaling so a post with score=1000 doesn't dominate
    score_component = min(math.log1p(max(post_score, 0)) * 8, 40)
    comment_component = min(math.log1p(max(num_comments, 0)) * 10, 35)
    ratio_component = upvote_ratio * 25  # 0-25 range

    return min(score_component + comment_component + ratio_component, 100.0)


def _score_recency(created_at: str) -> float:
    """Score 0-100 based on how recently the post was made.

    - Posts from the last hour score ~100.
    - Posts older than 7 days score ~0.
    """
    try:
        post_dt = datetime.fromisoformat(created_at)
        if post_dt.tzinfo is None:
            post_dt = post_dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return 0.0

    now = datetime.now(timezone.utc)
    age_hours = (now - post_dt).total_seconds() / 3600.0

    if age_hours <= 0:
        return 100.0
    if age_hours >= 168:  # 7 days
        return 0.0

    # Exponential decay: half-life of ~24 hours
    return max(0.0, min(100.0 * math.exp(-0.029 * age_hours), 100.0))


# ===================================================================
# LeadScoringTool
# ===================================================================

class LeadScoringTool(BaseTool):
    """Score a social media post as a potential lead (0-100).

    The composite score is a weighted average of four dimensions:
    ``pain_point_relevance``, ``purchase_intent``, ``influence_score``,
    and ``recency``.  Weights are loaded from the ``lead_scoring``
    section of ``target_audience.yaml``.
    """

    name: str = "lead_scoring"
    description: str = (
        "Score a social media post as a potential lead from 0-100. "
        "Input should be a JSON string representing a social post with at least "
        "'content' (str), 'created_at' (ISO datetime str), and 'engagement' (dict with "
        "score, num_comments, upvote_ratio). "
        "Returns a JSON object with the composite score and individual dimension scores."
    )

    def _run(self, argument: str) -> str:
        """Score the provided social post.

        Args:
            argument: JSON string with post data (matches :class:`SocialPost` shape).
        """
        try:
            post_data: dict[str, Any] = json.loads(argument)
        except (json.JSONDecodeError, TypeError):
            return json.dumps({"error": "Input must be a valid JSON string representing a social post."})

        content: str = post_data.get("content", "")
        created_at: str = post_data.get("created_at", "")
        engagement: dict = post_data.get("engagement", {})

        if not content:
            return json.dumps({"error": "'content' field is required."})

        # Load scoring weights from config
        scoring_config = _load_lead_scoring_config()
        weight_pain = scoring_config.get("pain_point_relevance", 0.40)
        weight_intent = scoring_config.get("purchase_intent", 0.30)
        weight_influence = scoring_config.get("influence_score", 0.20)
        weight_recency = scoring_config.get("recency", 0.10)

        # Load keyword / pain-point lists for relevance scoring
        keywords = _load_listening_keywords()
        pain_points = _load_pain_points()

        # Compute individual dimension scores
        pain_score = _score_pain_point_relevance(content, pain_points, keywords)
        intent_score = _score_purchase_intent(content)
        influence = _score_influence(engagement)
        recency = _score_recency(created_at)

        # Weighted composite
        composite = (
            weight_pain * pain_score
            + weight_intent * intent_score
            + weight_influence * influence
            + weight_recency * recency
        )
        composite = round(max(0.0, min(composite, 100.0)), 1)

        result = {
            "composite_score": composite,
            "pain_point_relevance": round(pain_score, 1),
            "purchase_intent": round(intent_score, 1),
            "influence_score": round(influence, 1),
            "recency": round(recency, 1),
            "weights": {
                "pain_point_relevance": weight_pain,
                "purchase_intent": weight_intent,
                "influence_score": weight_influence,
                "recency": weight_recency,
            },
            "min_score_to_engage": scoring_config.get("min_score_to_engage", 70),
            "qualifies_for_engagement": composite >= scoring_config.get("min_score_to_engage", 70),
            "qualifies_for_content": composite >= scoring_config.get("min_score_to_create_content", 50),
        }

        logger.info(
            "lead_scored",
            composite=composite,
            pain=round(pain_score, 1),
            intent=round(intent_score, 1),
            influence=round(influence, 1),
            recency=round(recency, 1),
            qualifies=result["qualifies_for_engagement"],
        )

        return json.dumps(result)
