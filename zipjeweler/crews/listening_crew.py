from crewai import Crew, Task
from zipjeweler.agents.listening.agents import (
    reddit_listener, twitter_listener, linkedin_listener,
    instagram_listener, facebook_listener, pinterest_listener, keyword_manager
)
from zipjeweler.config import DRY_RUN

PLATFORM_AGENTS = {
    "reddit": reddit_listener,
    "twitter": twitter_listener,
    "linkedin": linkedin_listener,
    "instagram": instagram_listener,
    "facebook": facebook_listener,
    "pinterest": pinterest_listener,
}

KEYWORDS = [
    "jewelry CAD software", "jewelry management", "jewelry inventory",
    "custom jewelry orders", "casting service", "jewelry production",
    "jewelry business software", "jeweler tools", "jewelry POS",
    "jewelry repair tracking", "goldsmith software",
]


class ListeningCrew:
    def __init__(self, platform: str = "all", dry_run: bool = None):
        self.platform = platform
        self.dry_run = dry_run if dry_run is not None else DRY_RUN

    def run(self):
        if self.dry_run:
            return [f"[DRY RUN] Would listen on {self.platform} for {len(KEYWORDS)} keywords"]

        agents = list(PLATFORM_AGENTS.values()) if self.platform == "all" else [PLATFORM_AGENTS[self.platform]]

        tasks = [
            Task(
                description=f"Search {agent.role.split()[0]} for posts mentioning: {', '.join(KEYWORDS[:5])}. Return top 10 opportunities with links and context.",
                agent=agent,
                expected_output="List of opportunities: [platform, url, text, relevance_score]",
            )
            for agent in agents
        ]

        crew = Crew(agents=agents + [keyword_manager], tasks=tasks, verbose=True)
        result = crew.kickoff()
        return result if isinstance(result, list) else [str(result)]
