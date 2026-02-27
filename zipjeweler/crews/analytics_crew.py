from crewai import Crew, Task
from zipjeweler.agents.analytics.agents import engagement_tracker, sentiment_analyst, insights_extractor
from zipjeweler.config import DRY_RUN


class AnalyticsCrew:
    def __init__(self, dry_run: bool = None):
        self.dry_run = dry_run if dry_run is not None else DRY_RUN

    def run(self):
        if self.dry_run:
            return "[DRY RUN] Analytics crew would collect and analyze metrics here."

        track_task = Task(
            description="Collect all engagement metrics from the past 24 hours across platforms. Update Google Sheets.",
            agent=engagement_tracker,
            expected_output="Metrics summary: impressions, engagements, follows, clicks per platform",
        )

        sentiment_task = Task(
            description="Analyze sentiment of all responses to ZipJeweler content and engagements in the past 24 hours.",
            agent=sentiment_analyst,
            expected_output="Sentiment report: positive/neutral/negative breakdown with notable patterns",
        )

        insights_task = Task(
            description="Extract top 5 actionable insights from today's metrics and sentiment. What should we do more/less of?",
            agent=insights_extractor,
            expected_output="5 actionable insights with supporting data and recommended next actions",
        )

        crew = Crew(
            agents=[engagement_tracker, sentiment_analyst, insights_extractor],
            tasks=[track_task, sentiment_task, insights_task],
            verbose=True,
        )
        return crew.kickoff()
