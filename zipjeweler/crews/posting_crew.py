from crewai import Crew, Task
from zipjeweler.agents.posting.agents import (
    scheduler, reddit_poster, twitter_poster,
    linkedin_poster, instagram_poster, facebook_poster
)
from zipjeweler.config import DRY_RUN


class PostingCrew:
    def __init__(self, dry_run: bool = None):
        self.dry_run = dry_run if dry_run is not None else DRY_RUN

    def run(self, approved_content: list = None):
        if self.dry_run:
            return "[DRY RUN] Posting crew would publish approved content here."

        approved_content = approved_content or []
        if not approved_content:
            return "No approved content to post."

        schedule_task = Task(
            description=f"Schedule {len(approved_content)} approved posts at optimal times across platforms.",
            agent=scheduler,
            expected_output="Publishing schedule with timestamps per platform",
        )

        crew = Crew(
            agents=[scheduler, reddit_poster, twitter_poster, linkedin_poster, instagram_poster, facebook_poster],
            tasks=[schedule_task],
            verbose=True,
        )
        return crew.kickoff()
