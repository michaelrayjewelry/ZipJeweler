"""CrewAI custom tools wrapping the Reddit platform."""

from __future__ import annotations

import json
from typing import Any

import structlog
from crewai.tools import BaseTool
from pydantic import Field

from zipjeweler.config.settings import get_settings
from zipjeweler.platforms.reddit import RedditPlatform

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Lazy singleton so we don't create a PRAW instance until a tool is called
# ---------------------------------------------------------------------------
_reddit_platform: RedditPlatform | None = None


def _get_reddit_platform() -> RedditPlatform:
    """Return a module-level :class:`RedditPlatform` singleton."""
    global _reddit_platform
    if _reddit_platform is None:
        _reddit_platform = RedditPlatform()
    return _reddit_platform


def _social_post_to_dict(post) -> dict:
    """Serialise a :class:`SocialPost` dataclass to a plain dict."""
    return {
        "platform": post.platform,
        "post_id": post.post_id,
        "author": post.author,
        "content": post.content,
        "url": post.url,
        "created_at": post.created_at,
        "engagement": post.engagement,
        "metadata": post.metadata,
    }


# ===================================================================
# RedditSearchTool
# ===================================================================
class RedditSearchTool(BaseTool):
    """Search Reddit for posts matching a query across configured subreddits."""

    name: str = "reddit_search"
    description: str = (
        "Search Reddit for posts matching a query across configured subreddits. "
        "Input should be a JSON string with 'query' (required) and 'limit' (optional, default 25). "
        "Returns a JSON list of matching posts with id, author, content, url, engagement, and metadata."
    )

    def _run(self, argument: str) -> str:
        """Execute the search.

        Args:
            argument: JSON string, e.g. ``{"query": "jewelry CAD", "limit": 10}``.
                      Also accepts a plain string which is treated as the query.
        """
        try:
            params = self._parse_input(argument)
        except Exception:
            # Treat the raw argument as a plain-text query
            params = {"query": argument.strip()}

        query: str = params.get("query", argument.strip())
        limit: int = int(params.get("limit", 25))

        if not query:
            return json.dumps({"error": "A 'query' parameter is required."})

        logger.info("reddit_search_tool_called", query=query, limit=limit)
        platform = _get_reddit_platform()

        try:
            posts = platform.search(query=query, limit=limit)
            results = [_social_post_to_dict(p) for p in posts]
            logger.info("reddit_search_tool_results", count=len(results))
            return json.dumps(results, default=str)
        except Exception as exc:
            logger.error("reddit_search_tool_error", error=str(exc))
            return json.dumps({"error": str(exc)})

    @staticmethod
    def _parse_input(argument: str) -> dict[str, Any]:
        """Try to parse *argument* as JSON; fall back to query-only dict."""
        return json.loads(argument)


# ===================================================================
# RedditMonitorTool
# ===================================================================
class RedditMonitorTool(BaseTool):
    """Monitor configured subreddits for new posts matching listening keywords."""

    name: str = "reddit_monitor"
    description: str = (
        "Monitor configured subreddits for new posts matching listening keywords. "
        "Input should be a JSON string with optional 'subreddits' (list), 'keywords' (list), "
        "and 'limit' (int, default 25). When omitted the values from target_audience.yaml are used. "
        "Returns a JSON list of matching posts."
    )

    def _run(self, argument: str = "") -> str:
        """Execute the monitoring scan.

        Args:
            argument: Optional JSON with override parameters.
        """
        params: dict[str, Any] = {}
        if argument and argument.strip():
            try:
                params = json.loads(argument)
            except (json.JSONDecodeError, TypeError):
                pass

        subreddits: list[str] | None = params.get("subreddits")
        keywords: list[str] | None = params.get("keywords")
        limit: int = int(params.get("limit", 25))

        logger.info(
            "reddit_monitor_tool_called",
            subreddits=subreddits,
            keywords_count=len(keywords) if keywords else "default",
            limit=limit,
        )
        platform = _get_reddit_platform()

        try:
            posts = platform.monitor_subreddits(
                subreddits=subreddits,
                keywords=keywords,
                limit=limit,
            )
            results = [_social_post_to_dict(p) for p in posts]
            logger.info("reddit_monitor_tool_results", count=len(results))
            return json.dumps(results, default=str)
        except Exception as exc:
            logger.error("reddit_monitor_tool_error", error=str(exc))
            return json.dumps({"error": str(exc)})


# ===================================================================
# RedditReplyTool
# ===================================================================
class RedditReplyTool(BaseTool):
    """Reply to a Reddit post or comment with dry_run support."""

    name: str = "reddit_reply"
    description: str = (
        "Reply to a Reddit post or comment. "
        "Input should be a JSON string with 'post_id' (required) and 'text' (required). "
        "Respects the dry_run setting — when True the reply is logged but not actually posted. "
        "Returns a JSON object with success status and the reply URL."
    )

    def _run(self, argument: str) -> str:
        """Execute the reply.

        Args:
            argument: JSON string with ``post_id`` and ``text``.
        """
        try:
            params = json.loads(argument)
        except (json.JSONDecodeError, TypeError):
            return json.dumps({"error": "Input must be a valid JSON string with 'post_id' and 'text'."})

        post_id: str = params.get("post_id", "").strip()
        text: str = params.get("text", "").strip()

        if not post_id or not text:
            return json.dumps({"error": "Both 'post_id' and 'text' are required."})

        settings = get_settings()
        logger.info(
            "reddit_reply_tool_called",
            post_id=post_id,
            text_length=len(text),
            dry_run=settings.dry_run,
        )
        platform = _get_reddit_platform()

        try:
            result = platform.reply_to_post(post_id=post_id, text=text)
            return json.dumps({
                "success": result.success,
                "post_url": result.post_url,
                "post_id": result.post_id,
                "error": result.error,
                "dry_run": settings.dry_run,
            })
        except Exception as exc:
            logger.error("reddit_reply_tool_error", error=str(exc))
            return json.dumps({"success": False, "error": str(exc)})


# ===================================================================
# RedditPostTool
# ===================================================================
class RedditPostTool(BaseTool):
    """Create a new Reddit post with dry_run support."""

    name: str = "reddit_post"
    description: str = (
        "Create a new Reddit submission. "
        "Input should be a JSON string with 'text' (required — first line is title, rest is body) "
        "and optional 'image_url'. "
        "Respects the dry_run setting — when True the post is logged but not actually submitted. "
        "Returns a JSON object with success status and the post URL."
    )

    def _run(self, argument: str) -> str:
        """Execute the post.

        Args:
            argument: JSON string with ``text`` and optional ``image_url``.
        """
        try:
            params = json.loads(argument)
        except (json.JSONDecodeError, TypeError):
            return json.dumps({"error": "Input must be a valid JSON string with 'text'."})

        text: str = params.get("text", "").strip()
        image_url: str = params.get("image_url", "").strip()

        if not text:
            return json.dumps({"error": "'text' is required. First line is the title, remainder is the body."})

        settings = get_settings()
        logger.info(
            "reddit_post_tool_called",
            text_length=len(text),
            image_url=image_url or None,
            dry_run=settings.dry_run,
        )
        platform = _get_reddit_platform()

        try:
            result = platform.post_content(text=text, image_url=image_url)
            return json.dumps({
                "success": result.success,
                "post_url": result.post_url,
                "post_id": result.post_id,
                "error": result.error,
                "dry_run": settings.dry_run,
            })
        except Exception as exc:
            logger.error("reddit_post_tool_error", error=str(exc))
            return json.dumps({"success": False, "error": str(exc)})
