"""Posting Crew — 6 agents: one scheduler + 5 platform posters."""
from crewai import Agent
from zipjeweler.config import BRAND_NAME

POST_BACKSTORY = (
    f"You publish approved {BRAND_NAME} content to your assigned platform at optimal times. "
    "You handle API calls, rate limits, media uploads, and confirm successful posting."
)

scheduler = Agent(
    role="Content Scheduler",
    goal="Manage the publishing calendar; queue approved content at optimal times per platform based on audience analytics",
    backstory=(
        "You own the content calendar. You know peak engagement windows for each platform "
        "and schedule posts to maximize reach without over-posting."
    ),
    verbose=True,
    allow_delegation=True,
)

reddit_poster = Agent(
    role="Reddit Publisher",
    goal=f"Post approved replies and content to Reddit on behalf of {BRAND_NAME}",
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

linkedin_poster = Agent(
    role="LinkedIn Publisher",
    goal=f"Post approved content and comments to LinkedIn on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

instagram_poster = Agent(
    role="Instagram Publisher",
    goal=f"Post approved content, stories, and reels to Instagram on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

facebook_poster = Agent(
    role="Facebook Publisher",
    goal=f"Post approved content to Facebook Groups and Pages on behalf of {BRAND_NAME}",
    backstory=POST_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)
