"""Reddit platform wrapper using PRAW."""

from __future__ import annotations

from datetime import datetime, timezone

import praw
import praw.exceptions
import prawcore.exceptions
import structlog
import yaml

from zipjeweler.config.settings import get_settings
from zipjeweler.platforms.base import PlatformBase, PostResult, SocialPost

logger = structlog.get_logger(__name__)


class RedditPlatform(PlatformBase):
    """Concrete Reddit implementation of :class:`PlatformBase`.

    Uses PRAW to interact with the Reddit API.  All write operations
    (``post_content``, ``reply_to_post``) respect ``settings.dry_run``.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._settings = settings
        self._reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
            username=settings.reddit_username,
            password=settings.reddit_password,
        )
        self._platform_config = self._load_platform_config()
        self._target_audience = self._load_target_audience()
        logger.info(
            "reddit_platform_initialized",
            username=settings.reddit_username,
            dry_run=settings.dry_run,
        )

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    def _load_platform_config(self) -> dict:
        """Load Reddit-specific section from platform_config.yaml."""
        config_path = self._settings.config_dir / "platform_config.yaml"
        try:
            with open(config_path) as fh:
                data = yaml.safe_load(fh)
            return data.get("platforms", {}).get("reddit", {})
        except FileNotFoundError:
            logger.warning("platform_config_not_found", path=str(config_path))
            return {}

    def _load_target_audience(self) -> dict:
        """Load target_audience.yaml for subreddit lists and keywords."""
        config_path = self._settings.config_dir / "target_audience.yaml"
        try:
            with open(config_path) as fh:
                return yaml.safe_load(fh) or {}
        except FileNotFoundError:
            logger.warning("target_audience_config_not_found", path=str(config_path))
            return {}

    @property
    def _subreddits(self) -> list[str]:
        """Return the configured list of subreddits to monitor."""
        return (
            self._target_audience
            .get("monitoring_locations", {})
            .get("reddit", {})
            .get("subreddits", [])
        )

    @property
    def _listening_keywords(self) -> list[str]:
        """Flatten all listening-topic keywords into a single list."""
        topics = self._target_audience.get("listening_topics", {})
        keywords: list[str] = []
        for topic in topics.values():
            keywords.extend(topic.get("keywords", []))
        return keywords

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _submission_to_social_post(submission: praw.models.Submission) -> SocialPost:
        """Convert a PRAW Submission to a :class:`SocialPost`."""
        created_dt = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
        return SocialPost(
            platform="reddit",
            post_id=submission.id,
            author=str(submission.author) if submission.author else "[deleted]",
            content=submission.selftext or submission.title,
            url=f"https://www.reddit.com{submission.permalink}",
            created_at=created_dt.isoformat(),
            engagement={
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
            },
            metadata={
                "subreddit": str(submission.subreddit),
                "title": submission.title,
                "is_self": submission.is_self,
                "link_flair_text": submission.link_flair_text,
                "over_18": submission.over_18,
            },
        )

    @staticmethod
    def _comment_to_social_post(comment: praw.models.Comment) -> SocialPost:
        """Convert a PRAW Comment to a :class:`SocialPost`."""
        created_dt = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
        return SocialPost(
            platform="reddit",
            post_id=comment.id,
            author=str(comment.author) if comment.author else "[deleted]",
            content=comment.body,
            url=f"https://www.reddit.com{comment.permalink}",
            created_at=created_dt.isoformat(),
            engagement={
                "score": comment.score,
            },
            metadata={
                "subreddit": str(comment.subreddit),
                "parent_id": comment.parent_id,
                "is_comment": True,
            },
        )

    # ------------------------------------------------------------------
    # PlatformBase implementation
    # ------------------------------------------------------------------

    def search(self, query: str, limit: int = 25) -> list[SocialPost]:
        """Search configured subreddits for *query*.

        Searches each monitored subreddit individually and aggregates
        results up to *limit*.
        """
        results: list[SocialPost] = []
        subreddits = self._subreddits
        if not subreddits:
            logger.warning("reddit_search_no_subreddits_configured")
            subreddits = ["all"]

        time_filter = (
            self._target_audience
            .get("monitoring_locations", {})
            .get("reddit", {})
            .get("time_filter", "week")
        )

        per_sub_limit = max(1, limit // len(subreddits))

        for sub_name in subreddits:
            if len(results) >= limit:
                break
            try:
                subreddit = self._reddit.subreddit(sub_name)
                for submission in subreddit.search(
                    query, sort="relevance", time_filter=time_filter, limit=per_sub_limit
                ):
                    results.append(self._submission_to_social_post(submission))
                    if len(results) >= limit:
                        break
                logger.debug(
                    "reddit_search_subreddit_done",
                    subreddit=sub_name,
                    query=query,
                    found=len(results),
                )
            except (prawcore.exceptions.PrawcoreException, praw.exceptions.PRAWException) as exc:
                logger.error(
                    "reddit_search_error",
                    subreddit=sub_name,
                    query=query,
                    error=str(exc),
                )

        logger.info("reddit_search_complete", query=query, total_results=len(results))
        return results[:limit]

    def get_recent_posts(self, source: str, limit: int = 25) -> list[SocialPost]:
        """Get the newest posts from subreddit *source*.

        Args:
            source: Subreddit name (without ``r/`` prefix).
            limit: Maximum posts to return.
        """
        results: list[SocialPost] = []
        try:
            subreddit = self._reddit.subreddit(source)
            for submission in subreddit.new(limit=limit):
                results.append(self._submission_to_social_post(submission))
            logger.info(
                "reddit_recent_posts",
                subreddit=source,
                count=len(results),
            )
        except (prawcore.exceptions.PrawcoreException, praw.exceptions.PRAWException) as exc:
            logger.error(
                "reddit_recent_posts_error",
                subreddit=source,
                error=str(exc),
            )
        return results

    def post_content(self, text: str, image_url: str = "") -> PostResult:
        """Submit a new post to the first configured subreddit.

        If ``settings.dry_run`` is ``True`` the post is logged but not
        actually submitted.

        The *text* argument should contain the title and body separated
        by a newline.  If no newline is present the entire string is
        used as the title and the body is empty.

        Args:
            text: Post content.  First line = title, remainder = body.
            image_url: Optional image URL to create a link post instead
                       of a self post.
        """
        parts = text.split("\n", 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""

        target_sub = self._subreddits[0] if self._subreddits else "test"

        if self._settings.dry_run:
            logger.info(
                "reddit_post_dry_run",
                subreddit=target_sub,
                title=title,
                body_length=len(body),
                image_url=image_url,
            )
            return PostResult(
                success=True,
                post_url=f"https://www.reddit.com/r/{target_sub}/dry_run",
                post_id="dry_run",
            )

        try:
            subreddit = self._reddit.subreddit(target_sub)
            if image_url:
                submission = subreddit.submit(title=title, url=image_url)
            else:
                submission = subreddit.submit(title=title, selftext=body)
            post_url = f"https://www.reddit.com{submission.permalink}"
            logger.info(
                "reddit_post_submitted",
                subreddit=target_sub,
                post_id=submission.id,
                url=post_url,
            )
            return PostResult(
                success=True,
                post_url=post_url,
                post_id=submission.id,
            )
        except (prawcore.exceptions.PrawcoreException, praw.exceptions.PRAWException) as exc:
            logger.error("reddit_post_error", error=str(exc))
            return PostResult(success=False, error=str(exc))

    def reply_to_post(self, post_id: str, text: str) -> PostResult:
        """Reply to a submission or comment identified by *post_id*.

        Attempts to resolve the id as a submission first; if that fails
        it tries to resolve it as a comment.

        If ``settings.dry_run`` is ``True`` the reply is logged but not
        actually submitted.
        """
        if self._settings.dry_run:
            logger.info(
                "reddit_reply_dry_run",
                post_id=post_id,
                reply_length=len(text),
                reply_preview=text[:200],
            )
            return PostResult(
                success=True,
                post_url=f"https://www.reddit.com/dry_run/{post_id}",
                post_id="dry_run",
            )

        try:
            # Try as a submission first
            try:
                submission = self._reddit.submission(id=post_id)
                # Access an attribute to force PRAW to fetch the object;
                # if the id is not a valid submission this will raise.
                _ = submission.title
                comment = submission.reply(text)
            except (prawcore.exceptions.NotFound, AttributeError):
                # Fall back to treating as a comment
                parent_comment = self._reddit.comment(id=post_id)
                comment = parent_comment.reply(text)

            reply_url = f"https://www.reddit.com{comment.permalink}"
            logger.info(
                "reddit_reply_posted",
                parent_id=post_id,
                reply_id=comment.id,
                url=reply_url,
            )
            return PostResult(
                success=True,
                post_url=reply_url,
                post_id=comment.id,
            )
        except (prawcore.exceptions.PrawcoreException, praw.exceptions.PRAWException) as exc:
            logger.error("reddit_reply_error", post_id=post_id, error=str(exc))
            return PostResult(success=False, error=str(exc))

    def get_post_metrics(self, post_id: str) -> dict:
        """Return score, num_comments, and upvote_ratio for a submission.

        If *post_id* resolves to a comment, only the score is returned.
        """
        try:
            try:
                submission = self._reddit.submission(id=post_id)
                _ = submission.title  # force fetch
                metrics = {
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "upvote_ratio": submission.upvote_ratio,
                    "is_submission": True,
                }
                logger.debug("reddit_metrics_fetched", post_id=post_id, metrics=metrics)
                return metrics
            except (prawcore.exceptions.NotFound, AttributeError):
                comment = self._reddit.comment(id=post_id)
                _ = comment.body  # force fetch
                metrics = {
                    "score": comment.score,
                    "is_submission": False,
                }
                logger.debug("reddit_metrics_fetched", post_id=post_id, metrics=metrics)
                return metrics
        except (prawcore.exceptions.PrawcoreException, praw.exceptions.PRAWException) as exc:
            logger.error("reddit_metrics_error", post_id=post_id, error=str(exc))
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Extra: subreddit monitoring
    # ------------------------------------------------------------------

    def monitor_subreddits(
        self,
        subreddits: list[str] | None = None,
        keywords: list[str] | None = None,
        limit: int = 25,
    ) -> list[SocialPost]:
        """Monitor multiple subreddits for new posts matching keywords.

        This is a convenience method that combines :meth:`get_recent_posts`
        across several subreddits and filters by keyword match.

        Args:
            subreddits: Subreddit names to scan.  Defaults to the configured
                        monitoring list from ``target_audience.yaml``.
            keywords: Keywords to match against title and body.  Defaults
                      to the aggregated listening-topic keywords.
            limit: Max posts to fetch per subreddit before filtering.

        Returns:
            Posts whose title or body contains at least one keyword.
        """
        subreddits = subreddits or self._subreddits
        keywords = keywords or self._listening_keywords

        if not subreddits:
            logger.warning("reddit_monitor_no_subreddits")
            return []
        if not keywords:
            logger.warning("reddit_monitor_no_keywords")
            return []

        # Lowercase keywords for case-insensitive matching
        kw_lower = [kw.lower() for kw in keywords]

        max_per_sub = (
            self._target_audience
            .get("monitoring_locations", {})
            .get("reddit", {})
            .get("max_posts_per_sub", limit)
        )

        matched: list[SocialPost] = []

        for sub_name in subreddits:
            try:
                subreddit = self._reddit.subreddit(sub_name)
                for submission in subreddit.new(limit=max_per_sub):
                    searchable = (
                        f"{submission.title} {submission.selftext}"
                    ).lower()
                    if any(kw in searchable for kw in kw_lower):
                        matched.append(self._submission_to_social_post(submission))
                logger.debug(
                    "reddit_monitor_subreddit_done",
                    subreddit=sub_name,
                    matched=len(matched),
                )
            except (prawcore.exceptions.PrawcoreException, praw.exceptions.PRAWException) as exc:
                logger.error(
                    "reddit_monitor_error",
                    subreddit=sub_name,
                    error=str(exc),
                )

        logger.info(
            "reddit_monitor_complete",
            subreddits_scanned=len(subreddits),
            keywords_count=len(keywords),
            total_matches=len(matched),
        )
        return matched
