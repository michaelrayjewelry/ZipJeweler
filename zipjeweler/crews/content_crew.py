from crewai import Crew, Task
from zipjeweler.agents.content.agents import copy_writer, image_director, ab_content_tester
from zipjeweler.config import DRY_RUN, BRAND_NAME


class ContentCrew:
    def __init__(self, platform: str = "all", dry_run: bool = None):
        self.platform = platform
        self.dry_run = dry_run if dry_run is not None else DRY_RUN

    def run(self):
        if self.dry_run:
            return "[DRY RUN] Content crew would generate posts and images here."

        copy_task = Task(
            description=f"Generate 3 platform-optimized posts for {self.platform} promoting {BRAND_NAME}. Include hooks, body, and CTAs.",
            agent=copy_writer,
            expected_output="3 complete post drafts with platform, hook, body, CTA, and hashtags",
        )

        image_task = Task(
            description=f"Create image generation prompts for the {self.platform} posts. Each prompt should produce a compelling jewelry business visual.",
            agent=image_director,
            expected_output="3 detailed image generation prompts aligned with each post",
        )

        ab_task = Task(
            description="Generate 2 alternative hooks for each post to enable A/B testing. Note what variable is being tested.",
            agent=ab_content_tester,
            expected_output="A/B variants for each post with testing hypothesis",
        )

        crew = Crew(
            agents=[copy_writer, image_director, ab_content_tester],
            tasks=[copy_task, image_task, ab_task],
            verbose=True,
        )
        return crew.kickoff()
