"""Abstract base class for all platform wrappers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SocialPost:
    """Represents a discovered social media post."""

    platform: str
    post_id: str
    author: str
    content: str
    url: str
    created_at: str  # ISO format
    engagement: dict = field(default_factory=dict)  # likes, comments, shares etc.
    metadata: dict = field(default_factory=dict)  # platform-specific extra data


@dataclass
class PostResult:
    """Result of posting or replying."""

    success: bool
    post_url: str = ""
    post_id: str = ""
    error: str = ""


class PlatformBase(ABC):
    """Abstract base class that every platform wrapper must implement.

    Each platform (Reddit, Twitter, LinkedIn, etc.) subclasses this and
    provides concrete implementations for searching, posting, replying,
    and gathering metrics.
    """

    @abstractmethod
    def search(self, query: str, limit: int = 25) -> list[SocialPost]:
        """Search the platform for posts matching *query*.

        Args:
            query: Free-text search string.
            limit: Maximum number of results to return.

        Returns:
            List of discovered social media posts.
        """
        ...

    @abstractmethod
    def get_recent_posts(self, source: str, limit: int = 25) -> list[SocialPost]:
        """Get the most recent posts from *source* (subreddit, feed, etc.).

        Args:
            source: Platform-specific source identifier (e.g. subreddit name).
            limit: Maximum number of results to return.

        Returns:
            List of recent social media posts.
        """
        ...

    @abstractmethod
    def post_content(self, text: str, image_url: str = "") -> PostResult:
        """Publish new content on the platform.

        Args:
            text: Body text of the post.
            image_url: Optional URL to an image to attach.

        Returns:
            PostResult indicating success or failure.
        """
        ...

    @abstractmethod
    def reply_to_post(self, post_id: str, text: str) -> PostResult:
        """Reply to an existing post or comment.

        Args:
            post_id: Platform-specific identifier of the post to reply to.
            text: Body text of the reply.

        Returns:
            PostResult indicating success or failure.
        """
        ...

    @abstractmethod
    def get_post_metrics(self, post_id: str) -> dict:
        """Retrieve engagement metrics for a given post.

        Args:
            post_id: Platform-specific identifier.

        Returns:
            Dictionary of metric name to value (e.g. score, comments, ratio).
        """
        ...
