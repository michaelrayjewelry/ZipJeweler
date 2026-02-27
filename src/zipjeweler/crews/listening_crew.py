"""Listening Crew — Social listening across all platforms + lead qualification."""

from pathlib import Path

import yaml
from crewai import Agent, Crew, Process, Task

from zipjeweler.config.settings import get_settings


def _load_yaml(filename: str) -> dict:
    base = Path(__file__).resolve().parent
    for subdir in ["config", "../agents/config"]:
        path = base / subdir / filename
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
    raise FileNotFoundError(f"YAML config not found: {filename}")


def _load_target_audience() -> dict:
    settings = get_settings()
    path = settings.config_dir / "target_audience.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def _read_directions() -> str:
    try:
        from zipjeweler.sheets.direction_reader import read_all_directions

        directions = read_all_directions()
        listening_directions = directions.get("listening", [])
        if listening_directions:
            return "\n".join(f"- {d}" for d in listening_directions)
    except Exception:
        pass
    return "No specific directions provided."


def create_listening_crew(platforms: list[str] | None = None) -> Crew:
    """Create the Listening Crew.

    Args:
        platforms: List of platforms to listen on. If None, uses all enabled platforms.
    """
    settings = get_settings()
    agent_configs = _load_yaml("listener_agents.yaml")
    task_configs = _load_yaml("listening_tasks.yaml")
    target_audience = _load_target_audience()
    user_direction = _read_directions()

    # Determine which platforms to activate
    all_platforms = ["reddit", "twitter", "linkedin", "facebook", "instagram", "pinterest"]
    active_platforms = platforms or all_platforms

    # Build subreddit list for Reddit
    reddit_locations = target_audience.get("monitoring_locations", {}).get("reddit", {})
    subreddits = ", ".join(
        f"r/{sub}" for sub in reddit_locations.get("subreddits", ["jewelers", "jewelrymaking"])
    )

    agents = []
    tasks = []

    # --- Platform-specific listener agents ---
    platform_agent_map = {
        "reddit": ("reddit_listener", "search_reddit"),
        "twitter": ("twitter_listener", "search_twitter"),
        "linkedin": ("linkedin_listener", "search_linkedin"),
        "facebook": ("facebook_listener", "search_facebook"),
        "instagram": ("instagram_listener", "search_instagram"),
        "pinterest": ("pinterest_listener", "search_pinterest"),
    }

    # Import tools conditionally based on platform
    tools_by_platform = {}
    if "reddit" in active_platforms:
        try:
            from zipjeweler.tools.reddit_tools import RedditMonitorTool, RedditSearchTool

            tools_by_platform["reddit"] = [RedditSearchTool(), RedditMonitorTool()]
        except Exception:
            tools_by_platform["reddit"] = []

    for platform in active_platforms:
        agent_key, task_key = platform_agent_map.get(platform, (None, None))
        if not agent_key or agent_key not in agent_configs:
            continue

        config = agent_configs[agent_key]
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=True,
            llm=settings.primary_model,
            tools=tools_by_platform.get(platform, []),
        )
        agents.append(agent)

        task_config = task_configs.get(task_key, {})
        if task_config:
            description = task_config["description"].format(
                subreddits=subreddits, user_direction=user_direction
            )
            task = Task(
                description=description,
                expected_output=task_config["expected_output"],
                agent=agent,
            )
            tasks.append(task)

    # --- Lead Qualifier Agent (always included) ---
    qualifier_config = agent_configs["lead_qualifier"]
    lead_qualifier = Agent(
        role=qualifier_config["role"],
        goal=qualifier_config["goal"],
        backstory=qualifier_config["backstory"],
        verbose=True,
        llm=settings.fast_model,
    )
    agents.append(lead_qualifier)

    qualify_config = task_configs.get("qualify_leads", {})
    if qualify_config:
        qualify_task = Task(
            description=qualify_config["description"].format(user_direction=user_direction),
            expected_output=qualify_config["expected_output"],
            agent=lead_qualifier,
            context=tasks,  # Qualifier sees all listener outputs
        )
        tasks.append(qualify_task)

    # --- Assemble Crew ---
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=True,
        embedder={
            "provider": "openai",
            "config": {"model": settings.embedding_model},
        },
    )

    return crew
