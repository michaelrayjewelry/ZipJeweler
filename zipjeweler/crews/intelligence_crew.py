from crewai import Crew, Task
from zipjeweler.agents.intelligence.agents import (
    daily_brief_agent, ai_answer_monitor_agent,
    competitor_tracker_agent, opportunity_scorer_agent
)
from zipjeweler.config import DRY_RUN


class IntelligenceCrew:
    def __init__(self, dry_run: bool = None):
        self.dry_run = dry_run if dry_run is not None else DRY_RUN

    def run_brief(self):
        brief_task = Task(
            description=(
                "Compile today's intelligence brief for ZipJeweler. "
                "Include: top opportunities spotted, competitor moves, AI platform gaps, "
                "and priority actions for other crews."
            ),
            agent=daily_brief_agent,
            expected_output="A structured daily brief with sections: Opportunities, Competitors, AI Gaps, Priority Actions",
        )

        monitor_task = Task(
            description="Check how major AI platforms (ChatGPT, Perplexity) answer 'best jewelry business management tools'",
            agent=ai_answer_monitor_agent,
            expected_output="Report on ZipJeweler's presence in AI answers and gaps to address",
        )

        crew = Crew(
            agents=[daily_brief_agent, ai_answer_monitor_agent, competitor_tracker_agent, opportunity_scorer_agent],
            tasks=[brief_task, monitor_task],
            verbose=not self.dry_run,
        )

        if self.dry_run:
            return "[DRY RUN] Intelligence brief would run here. Add API keys to execute."

        return crew.kickoff()

    def run(self):
        return self.run_brief()
