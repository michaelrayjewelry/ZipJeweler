"""Intelligence Crew — Daily brief, AI monitoring, competitor tracking."""

from pathlib import Path

import yaml
from crewai import Agent, Crew, Process, Task

from zipjeweler.config.settings import get_settings


def _load_yaml(filename: str) -> dict:
    """Load a YAML config file from the agents/config or crews/config directory."""
    base = Path(__file__).resolve().parent
    # Try crews/config first, then agents/config
    for subdir in ["config", "../agents/config"]:
        path = base / subdir / filename
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
    raise FileNotFoundError(f"YAML config not found: {filename}")


def _read_directions() -> str:
    """Read human directions from Google Sheets (if available)."""
    try:
        from zipjeweler.sheets.direction_reader import read_all_directions

        directions = read_all_directions()
        intelligence_directions = directions.get("intelligence", [])
        if intelligence_directions:
            return "\n".join(f"- {d}" for d in intelligence_directions)
    except Exception:
        pass
    return "No specific directions provided."


def create_intelligence_crew() -> Crew:
    """Create the Intelligence Crew for daily briefs and market monitoring."""
    settings = get_settings()

    agent_configs = _load_yaml("intelligence_agents.yaml")
    task_configs = _load_yaml("intelligence_tasks.yaml")
    user_direction = _read_directions()

    # --- Create Agents ---
    ai_monitor = Agent(
        role=agent_configs["ai_answer_monitor"]["role"],
        goal=agent_configs["ai_answer_monitor"]["goal"],
        backstory=agent_configs["ai_answer_monitor"]["backstory"],
        verbose=True,
        llm=settings.primary_model,
    )

    competitor_watcher = Agent(
        role=agent_configs["competitor_watcher"]["role"],
        goal=agent_configs["competitor_watcher"]["goal"],
        backstory=agent_configs["competitor_watcher"]["backstory"],
        verbose=True,
        llm=settings.primary_model,
    )

    opportunity_scorer = Agent(
        role=agent_configs["opportunity_scorer"]["role"],
        goal=agent_configs["opportunity_scorer"]["goal"],
        backstory=agent_configs["opportunity_scorer"]["backstory"],
        verbose=True,
        llm=settings.fast_model,
    )

    brief_generator = Agent(
        role=agent_configs["brief_generator"]["role"],
        goal=agent_configs["brief_generator"]["goal"],
        backstory=agent_configs["brief_generator"]["backstory"],
        verbose=True,
        llm=settings.primary_model,
    )

    # --- Create Tasks ---
    monitor_task = Task(
        description=task_configs["monitor_ai_answers"]["description"].format(
            user_direction=user_direction
        ),
        expected_output=task_configs["monitor_ai_answers"]["expected_output"],
        agent=ai_monitor,
    )

    competitor_task = Task(
        description=task_configs["watch_competitors"]["description"].format(
            user_direction=user_direction
        ),
        expected_output=task_configs["watch_competitors"]["expected_output"],
        agent=competitor_watcher,
    )

    scoring_task = Task(
        description=task_configs["score_opportunities"]["description"].format(
            user_direction=user_direction
        ),
        expected_output=task_configs["score_opportunities"]["expected_output"],
        agent=opportunity_scorer,
        context=[monitor_task, competitor_task],
    )

    brief_task = Task(
        description=task_configs["generate_daily_brief"]["description"].format(
            user_direction=user_direction
        ),
        expected_output=task_configs["generate_daily_brief"]["expected_output"],
        agent=brief_generator,
        context=[monitor_task, competitor_task, scoring_task],
    )

    # --- Assemble Crew ---
    crew = Crew(
        agents=[ai_monitor, competitor_watcher, opportunity_scorer, brief_generator],
        tasks=[monitor_task, competitor_task, scoring_task, brief_task],
        process=Process.sequential,
        verbose=True,
        memory=True,
        embedder={
            "provider": "openai",
            "config": {"model": settings.embedding_model},
        },
    )

    return crew
