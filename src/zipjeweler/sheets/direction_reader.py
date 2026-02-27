"""Aggregate human directions from every sheet tab into a single dict."""

from __future__ import annotations

import structlog

from zipjeweler.sheets import (
    creation_sheet,
    intelligence_sheet,
    learning_sheet,
    listening_sheet,
)

logger = structlog.get_logger(__name__)


def read_all_directions() -> dict[str, dict[int, str]]:
    """Read the Direction column from every sheet tab.

    Returns a dict keyed by domain name, where each value is a mapping of
    ``{row_id: direction_text}``.  Example::

        {
            "intelligence": {1: "Focus on competitor X", 4: "Dismiss"},
            "listening":    {12: "Prioritise this lead"},
            "creation":     {7: "Rewrite the intro paragraph"},
            "learning":     {3: "Investigate further"},
        }

    Any sheet that cannot be read (e.g. tab not yet created, API quota
    exceeded) is silently skipped -- the corresponding key will map to an
    empty dict.
    """
    results: dict[str, dict[int, str]] = {}

    readers: dict[str, object] = {
        "intelligence": intelligence_sheet,
        "listening": listening_sheet,
        "creation": creation_sheet,
        "learning": learning_sheet,
    }

    for name, module in readers.items():
        try:
            directions = module.read_directions()  # type: ignore[union-attr]
            results[name] = directions
            logger.debug(
                "direction_reader.read",
                sheet=name,
                count=len(directions),
            )
        except Exception:
            logger.exception(
                "direction_reader.read_failed",
                sheet=name,
            )
            results[name] = {}

    total = sum(len(v) for v in results.values())
    logger.info("direction_reader.all_read", total_directions=total)
    return results
