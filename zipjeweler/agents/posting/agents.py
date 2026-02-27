"""Posting Crew — 6 agents: scheduler + 5 platform publishers.
Platforms: Instagram, Facebook, X/Twitter, Pinterest, TikTok
"""
from crewai import Agent
from zipjeweler.config import BRAND_NAME

POST_BACKSTORY = (
    f"You publish approved {BRAND_NAME} content to your assigned platform at optimal times. "
    "You handle API calls, rate limits, media uploads, and confirm successful posting. "
    "All content links back to zipjeweler.com."
)

scheduler = Agent(
    role="Content Scheduler",
    goal="Manage the publishing calendar; queue approved content at optimal times per platform based on audience analytics",
    backstory=(
        "You own the content calendar across Instagram, Facebook, X, Pinterest, and TikTok. "
        "You know peak engagement windows and schedule posts to maximize reach without over-posting."
    ),
    verbose=True,
    allow_delegation=True,
)

instagram_poster = Agent(
    role="Instagram Publisher",
    goal=f"Post approved content, stories, reels, and carousels to Instagram on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

facebook_poster = Agent(
    role="Facebook Publisher",
    goal=f"Post approved content to Facebook Pages and Groups on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

twitter_poster = Agent(
    role="Twitter/X Publisher",
    goal=f"Post approved tweets, threads, and replies to Twitter/X on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

pinterest_poster = Agent(
    role="Pinterest Publisher",
    goal=f"Create and publish pins to relevant Pinterest boards on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

tiktok_poster = Agent(
    role="TikTok Publisher",
    goal=f"Post approved TikTok videos, captions, and engage with comments on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)
