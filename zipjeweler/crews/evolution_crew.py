from crewai import Crew, Task
from zipjeweler.agents.evolution.agents import (
    ab_test_runner, strategy_evolver, lead_nurturer,
    trend_detector, prompt_optimizer, timing_optimizer, autonomy_manager
)
from zipjeweler.config import DRY_RUN


class EvolutionCrew:
    def __init__(self, dry_run: bool = None):
        self.dry_run = dry_run if dry_run is not None else DRY_RUN

    def run(self, analytics_report: str = None):
        if self.dry_run:
            return "[DRY RUN] Evolution crew would analyze results and evolve strategy here."

        evolve_task = Task(
            description=f"Based on analytics: {analytics_report or 'no data yet'}, recommend strategic changes to improve performance.",
            agent=strategy_evolver,
            expected_output="Strategy update: what to change, why, and expected impact",
        )

        trend_task = Task(
            description="Identify emerging trends in jewelry industry conversations across monitored platforms.",
            agent=trend_detector,
            expected_output="Top 3 emerging trends with opportunity assessment",
        )

        timing_task = Task(
            description="Analyze posting performance data to refine optimal posting windows per platform.",
            agent=timing_optimizer,
            expected_output="Updated posting schedule recommendations per platform",
        )

        autonomy_task = Task(
            description="Review agent performance scores and recommend autonomy level adjustments.",
            agent=autonomy_manager,
            expected_output="Autonomy recommendations per crew with confidence scores",
        )

        crew = Crew(
            agents=[ab_test_runner, strategy_evolver, lead_nurturer,
                    trend_detector, prompt_optimizer, timing_optimizer, autonomy_manager],
            tasks=[evolve_task, trend_task, timing_task, autonomy_task],
            verbose=True,
        )
        return crew.kickoff()
