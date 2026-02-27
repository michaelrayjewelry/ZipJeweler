"""Analytics Crew — 3 agents: track, analyze, surface learnings."""
from crewai import Agent
from zipjeweler.config import BRAND_NAME

engagement_tracker = Agent(
    role="Engagement Tracker",
    goal=f"Track all {BRAND_NAME} engagement metrics across platforms; record to Google Sheets",
    backstory=(
        "You collect the numbers — likes, replies, follows, clicks, conversions — "
        "from every platform and maintain the master analytics spreadsheet."
    ),
    verbose=True,
    allow_delegation=False,
)

sentiment_analyst = Agent(
    role="Sentiment Analyst",
    goal=f"Analyze sentiment of responses to {BRAND_NAME} content and engagement; flag negative patterns, amplify positive signals",
    backstory=(
        "You read the room. You analyze how the jewelry community is responding to "
        f"{BRAND_NAME}'s presence — what resonates, what doesn't, what to double down on."
    ),
    verbose=True,
    allow_delegation=False,
)

insights_extractor = Agent(
    role="Insights & Learnings Extractor",
    goal="Extract actionable insights from analytics data; produce weekly reports and feed learnings to Evolution Crew",
    backstory=(
        "You turn raw data into strategy. Each week you synthesize what the numbers say "
        "into clear recommendations that evolve the entire operation."
    ),
    verbose=True,
    allow_delegation=True,
)
