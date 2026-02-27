"""Listening Crew — 7 agents: one per platform + keyword manager.
Platforms: Instagram, Facebook, X/Twitter, Pinterest, TikTok + Reddit (research only)
"""
from crewai import Agent
from zipjeweler.config import BRAND_NAME

LISTEN_BACKSTORY = (
    f"You are a specialized social listener for {BRAND_NAME}. "
    "You scan your assigned platform for jewelers discussing pain points — "
    "CAD software, casting services, custom orders, inventory, production management — "
    "and surface high-value posts for the Engagement Crew."
)

instagram_listener = Agent(
    role="Instagram Listener",
    goal="Monitor Instagram hashtags (#jewelrymaker, #goldsmith, #customjewelry, #jewelrybusiness) and comments for ZipJeweler opportunities",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

facebook_listener = Agent(
    role="Facebook Listener",
    goal="Monitor Facebook Groups for jewelers (Jewelry Making, Goldsmithing, Custom Jewelry Business) for ZipJeweler opportunities",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

twitter_listener = Agent(
    role="Twitter/X Listener",
    goal="Monitor Twitter/X for jewelers discussing business pain points, CAD tools, inventory, and production challenges",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

pinterest_listener = Agent(
    role="Pinterest Listener",
    goal="Monitor Pinterest for jewelry makers and business owners searching for tools and resources; identify ZipJeweler opportunities",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

tiktok_listener = Agent(
    role="TikTok Listener",
    goal="Monitor TikTok for jewelry maker content creators discussing their business challenges; identify ZipJeweler opportunities in comments and creator communities",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

reddit_listener = Agent(
    role="Reddit Research Listener",
    goal="Monitor r/jewelry, r/jewelrymaking, r/goldsmith for jeweler pain points and business discussions that inform ZipJeweler messaging strategy",
    backstory=LISTEN_BACKSTORY + " Reddit is used for research and messaging intelligence, not primary engagement.",
    verbose=True,
    allow_delegation=False,
)

keyword_manager = Agent(
    role="Keyword Strategy Manager",
    goal="Maintain and evolve the master keyword list used by all listeners; add new signals, retire low-signal terms based on Evolution Crew learnings",
    backstory=(
        "You manage the semantic map of how jewelers talk about their pain points. "
        "You evolve keywords based on what the Evolution Crew learns works best."
    ),
    verbose=True,
    allow_delegation=True,
)
