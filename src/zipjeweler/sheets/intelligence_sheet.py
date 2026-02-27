"""Sync Intelligence model data to/from the 'Intelligence -- Daily Brief' tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gspread
import structlog

from zipjeweler.sheets.client import get_or_create_worksheet

if TYPE_CHECKING:
    from zipjeweler.models.learning import Intelligence

logger = structlog.get_logger(__name__)

TAB_NAME = "Intelligence \u2014 Daily Brief"

HEADERS = [
    "ID",
    "Date",
    "Type",
    "Description",
    "Dollar Value",
    "Priority",
    "Competitor",
    "Source",
    "Draft Content",
    "Status",
    "Direction",
]

# Column index for the Direction column (1-based).
_DIRECTION_COL = HEADERS.index("Direction") + 1


def _item_to_row(item: Intelligence) -> list[str]:
    """Convert an Intelligence ORM instance to a flat row of strings."""
    return [
        str(item.id),
        str(item.date or ""),
        str(item.type or ""),
        str(item.description or ""),
        str(item.dollar_value or 0.0),
        str(item.priority or 3),
        str(item.competitor or ""),
        str(item.source or ""),
        str(item.draft_content or ""),
        str(item.status or "new"),
        str(item.direction or ""),
    ]


def sync_intelligence_to_sheet(items: list[Intelligence]) -> int:
    """Write Intelligence items to the Google Sheet, upserting by ID.

    Existing rows whose ID matches are overwritten; new items are appended.

    Parameters:
        items: A list of :class:`Intelligence` ORM objects.

    Returns:
        The number of rows written or updated.
    """
    try:
        ws = get_or_create_worksheet(TAB_NAME, HEADERS)
    except Exception:
        logger.exception("intelligence_sheet.get_worksheet_failed")
        return 0

    try:
        existing_data = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("intelligence_sheet.read_failed")
        return 0

    # Build a map of ID -> sheet row number (1-based, skipping header).
    id_col = HEADERS.index("ID")
    id_to_row: dict[str, int] = {}
    for idx, row in enumerate(existing_data[1:], start=2):  # row 2 onwards
        if row and len(row) > id_col and row[id_col]:
            id_to_row[row[id_col]] = idx

    rows_written = 0
    batch_updates: list[dict] = []
    append_rows: list[list[str]] = []

    for item in items:
        row_data = _item_to_row(item)
        item_id = str(item.id)

        if item_id in id_to_row:
            sheet_row = id_to_row[item_id]
            range_str = f"A{sheet_row}:{gspread.utils.rowcol_to_a1(sheet_row, len(HEADERS))}"
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
            "intelligence_sheet.synced",
            updated=len(batch_updates),
            appended=len(append_rows),
        )
    except gspread.exceptions.APIError:
        logger.exception("intelligence_sheet.write_failed")
        return 0

    return rows_written


def read_directions() -> dict[int, str]:
    """Read human-provided directions from the sheet.

    Returns:
        A mapping of ``{intelligence_id: direction_text}`` for every row whose
        *Direction* column is non-empty.
    """
    try:
        ws = get_or_create_worksheet(TAB_NAME, HEADERS)
    except Exception:
        logger.exception("intelligence_sheet.get_worksheet_failed")
        return {}

    try:
        all_rows = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("intelligence_sheet.read_directions_failed")
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

    logger.info(
        "intelligence_sheet.directions_read",
        count=len(directions),
    )
    return directions
