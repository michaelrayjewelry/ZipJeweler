"""Listening Crew — 7 agents: one per platform + a keyword manager."""
from crewai import Agent
from zipjeweler.config import BRAND_NAME

LISTEN_BACKSTORY = (
    f"You are a specialized social listener for {BRAND_NAME}. "
    "You scan your assigned platform for jewelers discussing pain points — "
    "CAD software, casting services, custom orders, inventory, production management — "
    "and surface high-value threads for the Engagement Crew."
)

reddit_listener = Agent(
    role="Reddit Listener",
    goal="Monitor r/jewelry, r/jewelrymaking, r/goldsmith, r/metalworking and relevant subreddits for ZipJeweler opportunities",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

twitter_listener = Agent(
    role="Twitter/X Listener",
    goal="Monitor Twitter/X for jewelers discussing business pain points, CAD tools, and production challenges",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

linkedin_listener = Agent(
    role="LinkedIn Listener",
    goal="Monitor LinkedIn for jewelry business professionals discussing operational challenges",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

instagram_listener = Agent(
    role="Instagram Listener",
    goal="Monitor Instagram hashtags and comments in the jewelry maker community for ZipJeweler opportunities",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

facebook_listener = Agent(
    role="Facebook Listener",
    goal="Monitor Facebook Groups for jewelers (Jewelry Making, Goldsmithing, Custom Jewelry) for ZipJeweler opportunities",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

pinterest_listener = Agent(
    role="Pinterest Listener",
    goal="Monitor Pinterest for jewelry makers and business owners who may need ZipJeweler",
    backstory=LISTEN_BACKSTORY,
    verbose=True,
    allow_delegation=False,
)

keyword_manager = Agent(
    role="Keyword Strategy Manager",
    goal="Maintain and evolve the master keyword list used by all listeners; add new signals, retire low-signal terms",
    backstory=(
        "You manage the semantic map of how jewelers talk about their pain points. "
        "You evolve keywords based on what the Evolution Crew learns works best."
    ),
    verbose=True,
    allow_delegation=True,
)
