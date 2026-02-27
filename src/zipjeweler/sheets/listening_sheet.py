"""Sync Lead model data to/from the 'Listening -- Leads' tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gspread
import structlog

from zipjeweler.sheets.client import get_or_create_worksheet

if TYPE_CHECKING:
    from gspread import Worksheet

    from zipjeweler.models.lead import Lead

logger = structlog.get_logger(__name__)

TAB_NAME = "Listening \u2014 Leads"

HEADERS = [
    "ID",
    "Created At",
    "Platform",
    "Source URL",
    "Author",
    "Content Snippet",
    "Topic Category",
    "Audience Segment",
    "Pain Points",
    "Lead Score",
    "Dollar Value",
    "Pain Point Relevance",
    "Purchase Intent",
    "Influence Score",
    "Nurture Stage",
    "Last Engagement",
    "Engagement Count",
    "Status",
    "Reply Drafted",
    "Notes",
    "Direction",
]

_DIRECTION_COL = HEADERS.index("Direction") + 1
_STATUS_COL = HEADERS.index("Status") + 1


def _lead_to_row(lead: Lead) -> list[str]:
    """Convert a Lead ORM instance to a flat row of strings."""
    return [
        str(lead.id),
        str(lead.created_at or ""),
        str(lead.platform or ""),
        str(lead.source_url or ""),
        str(lead.author or ""),
        str(lead.content_snippet or ""),
        str(lead.topic_category or ""),
        str(lead.audience_segment or ""),
        str(lead.pain_points_detected or ""),
        str(lead.lead_score or 0),
        str(lead.dollar_value or 0.0),
        str(lead.pain_point_relevance or 0.0),
        str(lead.purchase_intent or 0.0),
        str(lead.influence_score or 0.0),
        str(lead.nurture_stage or "discovery"),
        str(lead.last_engagement_at or ""),
        str(lead.engagement_count or 0),
        str(lead.status or "new"),
        str(lead.reply_drafted or ""),
        str(lead.notes or ""),
        "",  # Direction -- never overwrite human input
    ]


def _get_worksheet() -> Worksheet:
    return get_or_create_worksheet(TAB_NAME, HEADERS)


def sync_leads_to_sheet(leads: list[Lead]) -> int:
    """Write Lead items to the Google Sheet, upserting by ID.

    The *Direction* column is intentionally left untouched for existing rows
    so that human-provided directions are never overwritten.

    Parameters:
        leads: A list of :class:`Lead` ORM objects.

    Returns:
        The number of rows written or updated.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("listening_sheet.get_worksheet_failed")
        return 0

    try:
        existing_data = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("listening_sheet.read_failed")
        return 0

    id_col = HEADERS.index("ID")
    dir_col = HEADERS.index("Direction")
    id_to_row: dict[str, int] = {}
    id_to_direction: dict[str, str] = {}
    for idx, row in enumerate(existing_data[1:], start=2):
        if row and len(row) > id_col and row[id_col]:
            id_to_row[row[id_col]] = idx
            if len(row) > dir_col:
                id_to_direction[row[id_col]] = row[dir_col]

    batch_updates: list[dict] = []
    append_rows: list[list[str]] = []
    rows_written = 0

    for lead in leads:
        row_data = _lead_to_row(lead)
        lead_id = str(lead.id)

        if lead_id in id_to_row:
            # Preserve existing direction value.
            row_data[dir_col] = id_to_direction.get(lead_id, "")
            sheet_row = id_to_row[lead_id]
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
            "listening_sheet.synced",
            updated=len(batch_updates),
            appended=len(append_rows),
        )
    except gspread.exceptions.APIError:
        logger.exception("listening_sheet.write_failed")
        return 0

    return rows_written


def read_directions() -> dict[int, str]:
    """Read human-provided directions from the Direction column.

    Returns:
        A mapping of ``{lead_id: direction_text}`` for every row whose
        *Direction* column is non-empty.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("listening_sheet.get_worksheet_failed")
        return {}

    try:
        all_rows = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("listening_sheet.read_directions_failed")
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
                lead_id = int(row[id_col])
            except (ValueError, TypeError):
                continue
            directions[lead_id] = direction

    logger.info("listening_sheet.directions_read", count=len(directions))
    return directions


def update_lead_status(row: int, status: str) -> bool:
    """Update the Status cell for a specific sheet row.

    Parameters:
        row:    The 1-based sheet row number (including header, so the first
                data row is 2).
        status: New status value, e.g. ``"replied"``, ``"converted"``.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("listening_sheet.get_worksheet_failed")
        return False

    try:
        ws.update_cell(row, _STATUS_COL, status)
        logger.info(
            "listening_sheet.status_updated",
            row=row,
            status=status,
        )
        return True
    except gspread.exceptions.APIError:
        logger.exception(
            "listening_sheet.status_update_failed",
            row=row,
            status=status,
        )
        return False
