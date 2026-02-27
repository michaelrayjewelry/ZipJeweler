"""Sync Learning model data to/from the 'Learning -- Insights' tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gspread
import structlog

from zipjeweler.sheets.client import get_or_create_worksheet

if TYPE_CHECKING:
    from gspread import Worksheet

    from zipjeweler.models.learning import Learning

logger = structlog.get_logger(__name__)

TAB_NAME = "Learning \u2014 Insights"

HEADERS = [
    "ID",
    "Created At",
    "Last Validated",
    "Category",
    "Insight",
    "Evidence",
    "Confidence",
    "Applied",
    "Direction",
]

_DIRECTION_COL = HEADERS.index("Direction") + 1


def _learning_to_row(item: Learning) -> list[str]:
    """Convert a Learning ORM instance to a flat row of strings."""
    return [
        str(item.id),
        str(item.created_at or ""),
        str(item.last_validated or ""),
        str(item.category or ""),
        str(item.insight or ""),
        str(item.evidence or ""),
        str(item.confidence or 0.0),
        str(item.applied) if item.applied is not None else "False",
        "",  # Direction -- never overwrite human input
    ]


def _get_worksheet() -> Worksheet:
    return get_or_create_worksheet(TAB_NAME, HEADERS)


def sync_learnings_to_sheet(items: list[Learning]) -> int:
    """Write Learning items to the Google Sheet, upserting by ID.

    The *Direction* column for existing rows is preserved so human input is
    never overwritten.

    Parameters:
        items: A list of :class:`Learning` ORM objects.

    Returns:
        The number of rows written or updated.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("learning_sheet.get_worksheet_failed")
        return 0

    try:
        existing_data = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("learning_sheet.read_failed")
        return 0

    id_col = HEADERS.index("ID")
    dir_col = HEADERS.index("Direction")

    id_to_row: dict[str, int] = {}
    id_to_direction: dict[str, str] = {}

    for idx, row in enumerate(existing_data[1:], start=2):
        if row and len(row) > id_col and row[id_col]:
            rid = row[id_col]
            id_to_row[rid] = idx
            if len(row) > dir_col:
                id_to_direction[rid] = row[dir_col]

    batch_updates: list[dict] = []
    append_rows: list[list[str]] = []
    rows_written = 0

    for item in items:
        row_data = _learning_to_row(item)
        item_id = str(item.id)

        if item_id in id_to_row:
            # Preserve existing direction value.
            row_data[dir_col] = id_to_direction.get(item_id, "")
            sheet_row = id_to_row[item_id]
            end_col = gspread.utils.rowcol_to_a1(sheet_row, len(HEADERS))
            range_str = f"A{sheet_row}:{end_col}"
            batch_updates.append({"range": range_str, "values": [row_data]})
        else:
            append_rows.append(row_data)

        rows_written += 1

    try:
        if batch_updates:
            ws.batch_update(batch_updates, value_input_option="USER_ENTERED")
        if append_rows:
            ws.append_rows(append_rows, value_input_option="USER_ENTERED")
        logger.info(
            "learning_sheet.synced",
            updated=len(batch_updates),
            appended=len(append_rows),
        )
    except gspread.exceptions.APIError:
        logger.exception("learning_sheet.write_failed")
        return 0

    return rows_written


def read_directions() -> dict[int, str]:
    """Read human-provided directions from the Direction column.

    Returns:
        A mapping of ``{learning_id: direction_text}`` for every row whose
        *Direction* column is non-empty.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("learning_sheet.get_worksheet_failed")
        return {}

    try:
        all_rows = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("learning_sheet.read_directions_failed")
        return {}

    id_col = HEADERS.index("ID")
    dir_col = HEADERS.index("Direction")

    directions: dict[int, str] = {}
    for row in all_rows[1:]:
        if len(row) <= max(id_col, dir_col):
            continue
        direction = row[dir_col].strip()
        if direction:
            try:
                item_id = int(row[id_col])
            except (ValueError, TypeError):
                continue
            directions[item_id] = direction

    logger.info("learning_sheet.directions_read", count=len(directions))
    return directions
