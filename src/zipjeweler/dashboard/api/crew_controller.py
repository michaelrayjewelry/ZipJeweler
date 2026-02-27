"""Crew controller — Start/stop/configure crews from the dashboard."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import streamlit as st


class CrewState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class CrewRun:
    crew_name: str
    state: CrewState = CrewState.IDLE
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str = ""
    result_summary: str = ""


def _get_crew_registry() -> dict[str, CrewRun]:
    """Get or initialize the crew registry in session state."""
    if "crew_registry" not in st.session_state:
        st.session_state.crew_registry = {
            name: CrewRun(crew_name=name)
            for name in [
                "Intelligence", "Listening", "Engagement",
                "Content", "Posting", "Analytics", "Evolution",
            ]
        }
    return st.session_state.crew_registry


def get_crew_state(crew_name: str) -> CrewState:
    registry = _get_crew_registry()
    run = registry.get(crew_name)
    return run.state if run else CrewState.IDLE


def get_all_crew_states() -> dict[str, CrewState]:
    registry = _get_crew_registry()
    return {name: run.state for name, run in registry.items()}


def start_crew(crew_name: str, dry_run: bool = True) -> str:
    """Start a crew run. Returns status message."""
    registry = _get_crew_registry()
    run = registry.get(crew_name)
    if not run:
        return f"Unknown crew: {crew_name}"

    if run.state == CrewState.RUNNING:
        return f"{crew_name} Crew is already running"

    run.state = CrewState.RUNNING
    run.started_at = datetime.utcnow()
    run.error = ""
    run.result_summary = ""

    # Update session state for the agent_status component
    if "crew_statuses" in st.session_state:
        st.session_state.crew_statuses[crew_name] = "running"

    return f"{crew_name} Crew started (dry_run={dry_run})"


def stop_crew(crew_name: str) -> str:
    """Stop a crew run. Returns status message."""
    registry = _get_crew_registry()
    run = registry.get(crew_name)
    if not run:
        return f"Unknown crew: {crew_name}"

    run.state = CrewState.IDLE
    run.finished_at = datetime.utcnow()

    if "crew_statuses" in st.session_state:
        st.session_state.crew_statuses[crew_name] = "idle"

    return f"{crew_name} Crew stopped"


def stop_all_crews() -> str:
    """Stop all running crews."""
    registry = _get_crew_registry()
    stopped = []
    for name, run in registry.items():
        if run.state == CrewState.RUNNING:
            run.state = CrewState.IDLE
            run.finished_at = datetime.utcnow()
            stopped.append(name)

    if "crew_statuses" in st.session_state:
        for name in st.session_state.crew_statuses:
            st.session_state.crew_statuses[name] = "idle"

    return f"Stopped {len(stopped)} crews: {', '.join(stopped) or 'none running'}"


def mark_crew_error(crew_name: str, error: str) -> None:
    """Mark a crew as errored."""
    registry = _get_crew_registry()
    run = registry.get(crew_name)
    if run:
        run.state = CrewState.ERROR
        run.error = error
        run.finished_at = datetime.utcnow()
        if "crew_statuses" in st.session_state:
            st.session_state.crew_statuses[crew_name] = "error"


def mark_crew_complete(crew_name: str, summary: str = "") -> None:
    """Mark a crew run as complete."""
    registry = _get_crew_registry()
    run = registry.get(crew_name)
    if run:
        run.state = CrewState.IDLE
        run.result_summary = summary
        run.finished_at = datetime.utcnow()
        if "crew_statuses" in st.session_state:
            st.session_state.crew_statuses[crew_name] = "idle"


def get_crew_history(crew_name: str) -> dict | None:
    """Get the last run info for a crew."""
    registry = _get_crew_registry()
    run = registry.get(crew_name)
    if not run:
        return None
    return {
        "crew_name": run.crew_name,
        "state": run.state.value,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "error": run.error,
        "result_summary": run.result_summary,
    }
