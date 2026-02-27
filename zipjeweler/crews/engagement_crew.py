from crewai import Crew, Task
from zipjeweler.agents.engagement.agents import (
    reddit_engager, twitter_engager, linkedin_engager,
    instagram_engager, facebook_engager, approval_manager, dm_nurture_agent
)
from zipjeweler.config import DRY_RUN, APPROVAL_REQUIRED


class EngagementCrew:
    def __init__(self, dry_run: bool = None):
        self.dry_run = dry_run if dry_run is not None else DRY_RUN

    def run(self, leads: list = None):
        if self.dry_run:
            return "[DRY RUN] Engagement crew would craft and post replies here."

        leads = leads or []
        tasks = []

        for lead in leads:
            platform = lead.get("platform", "reddit")
            agent_map = {
                "reddit": reddit_engager, "twitter": twitter_engager,
                "linkedin": linkedin_engager, "instagram": instagram_engager,
                "facebook": facebook_engager,
            }
            engager = agent_map.get(platform, reddit_engager)

            draft_task = Task(
                description=f"Craft a helpful reply to this {platform} post: {lead.get('text', '')}. Naturally mention ZipJeweler.",
                agent=engager,
                expected_output="A natural, helpful reply that mentions ZipJeweler without being spammy",
            )
            tasks.append(draft_task)

        if APPROVAL_REQUIRED:
            review_task = Task(
                description="Review all drafted replies for quality, brand alignment, and spam risk. Approve or revise each.",
                agent=approval_manager,
                expected_output="Approved list of replies ready to post",
            )
            tasks.append(review_task)

        if not tasks:
            return "No leads to engage with."

        crew = Crew(
            agents=[reddit_engager, twitter_engager, linkedin_engager,
                    instagram_engager, facebook_engager, approval_manager, dm_nurture_agent],
            tasks=tasks,
            verbose=True,
        )
        return crew.kickoff()
