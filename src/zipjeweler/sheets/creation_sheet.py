"""Sync Content model data to/from the 'Creation -- Content Drafts' tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gspread
import structlog

from zipjeweler.sheets.client import get_or_create_worksheet

if TYPE_CHECKING:
    from gspread import Worksheet

    from zipjeweler.models.content import Content

logger = structlog.get_logger(__name__)

TAB_NAME = "Creation \u2014 Content Drafts"

HEADERS = [
    "ID",
    "Created At",
    "Updated At",
    "Target Platform",
    "Content Type",
    "Text Draft",
    "Image URL",
    "Image Prompt",
    "Based On Lead ID",
    "Strategy Notes",
    "Topic Category",
    "A/B Variant",
    "A/B Test Group",
    "Status",
    "Human Edits",
    "Direction",
]

_DIRECTION_COL = HEADERS.index("Direction") + 1
_STATUS_COL = HEADERS.index("Status") + 1


def _content_to_row(item: Content) -> list[str]:
    """Convert a Content ORM instance to a flat row of strings."""
    return [
        str(item.id),
        str(item.created_at or ""),
        str(item.updated_at or ""),
        str(item.target_platform or ""),
        str(item.content_type or ""),
        str(item.text_draft or ""),
        str(item.image_url or ""),
        str(item.image_prompt or ""),
        str(item.based_on_lead_id or ""),
        str(item.strategy_notes or ""),
        str(item.topic_category or ""),
        str(item.ab_variant or ""),
        str(item.ab_test_group or ""),
        str(item.status or "draft"),
        str(item.human_edits or ""),
        "",  # Direction -- never overwrite human input
    ]


def _get_worksheet() -> Worksheet:
    return get_or_create_worksheet(TAB_NAME, HEADERS)


def sync_content_to_sheet(items: list[Content]) -> int:
    """Write Content items to the Google Sheet, upserting by ID.

    The *Direction* and *Human Edits* columns for existing rows are preserved
    so that manual edits from the sheet are never overwritten.

    Parameters:
        items: A list of :class:`Content` ORM objects.

    Returns:
        The number of rows written or updated.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("creation_sheet.get_worksheet_failed")
        return 0

    try:
        existing_data = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("creation_sheet.read_failed")
        return 0

    id_col = HEADERS.index("ID")
    dir_col = HEADERS.index("Direction")
    edits_col = HEADERS.index("Human Edits")
    status_col = HEADERS.index("Status")

    id_to_row: dict[str, int] = {}
    id_to_preserved: dict[str, dict[str, str]] = {}

    for idx, row in enumerate(existing_data[1:], start=2):
        if row and len(row) > id_col and row[id_col]:
            rid = row[id_col]
            id_to_row[rid] = idx
            id_to_preserved[rid] = {
                "direction": row[dir_col] if len(row) > dir_col else "",
                "human_edits": row[edits_col] if len(row) > edits_col else "",
                "status": row[status_col] if len(row) > status_col else "",
            }

    batch_updates: list[dict] = []
    append_rows: list[list[str]] = []
    rows_written = 0

    for item in items:
        row_data = _content_to_row(item)
        item_id = str(item.id)

        if item_id in id_to_row:
            preserved = id_to_preserved[item_id]
            # Keep the human-edited direction.
            row_data[dir_col] = preserved["direction"]
            # If the sheet has human edits, preserve them.
            sheet_edits = preserved["human_edits"].strip()
            if sheet_edits:
                row_data[edits_col] = sheet_edits
            # If the sheet status was set to approved/rejected by a human,
            # keep that status rather than overwriting with the DB value.
            sheet_status = preserved["status"].strip().lower()
            if sheet_status in ("approved", "rejected", "edited"):
                row_data[status_col] = preserved["status"]

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
            "creation_sheet.synced",
            updated=len(batch_updates),
            appended=len(append_rows),
        )
    except gspread.exceptions.APIError:
        logger.exception("creation_sheet.write_failed")
        return 0

    return rows_written


def read_directions() -> dict[int, str]:
    """Read human-provided directions from the Direction column.

    Returns:
        A mapping of ``{content_id: direction_text}`` for every row whose
        *Direction* column is non-empty.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("creation_sheet.get_worksheet_failed")
        return {}

    try:
        all_rows = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("creation_sheet.read_directions_failed")
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

    logger.info("creation_sheet.directions_read", count=len(directions))
    return directions


def get_approved_content() -> list[dict[str, str]]:
    """Return all rows from the sheet whose status is 'approved' or 'edited'.

    This allows a human to approve content in the spreadsheet; the poster
    agent can then pick up those items for publishing.

    Returns:
        A list of dicts keyed by header name for every approved/edited row.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("creation_sheet.get_worksheet_failed")
        return []

    try:
        all_rows = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("creation_sheet.read_approved_failed")
        return []

    if len(all_rows) < 2:
        return []

    header = all_rows[0]
    status_col = HEADERS.index("Status")
    approved: list[dict[str, str]] = []

    for row in all_rows[1:]:
        if len(row) <= status_col:
            continue
        if row[status_col].strip().lower() in ("approved", "edited"):
            record = {header[i]: (row[i] if i < len(row) else "") for i in range(len(header))}
            approved.append(record)

    logger.info("creation_sheet.approved_content_read", count=len(approved))
    return approved
