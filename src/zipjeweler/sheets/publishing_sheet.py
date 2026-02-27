"""Sync Engagement model data to/from the 'Publishing -- Posts' tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gspread
import structlog

from zipjeweler.sheets.client import get_or_create_worksheet

if TYPE_CHECKING:
    from gspread import Worksheet

    from zipjeweler.models.engagement import Engagement

logger = structlog.get_logger(__name__)

TAB_NAME = "Publishing \u2014 Posts"

HEADERS = [
    "ID",
    "Created At",
    "Updated At",
    "Content ID",
    "Platform",
    "Post URL",
    "Post Type",
    "Likes",
    "Shares",
    "Comments",
    "Clicks",
    "Impressions",
    "Engagement Rate",
    "Positive Responses",
    "Negative Responses",
    "Question Responses",
    "Sentiment Summary",
    "A/B Variant",
    "A/B Test Group",
    "Status",
]


def _post_to_row(post: Engagement) -> list[str]:
    """Convert an Engagement ORM instance to a flat row of strings."""
    return [
        str(post.id),
        str(post.created_at or ""),
        str(post.updated_at or ""),
        str(post.content_id or ""),
        str(post.platform or ""),
        str(post.post_url or ""),
        str(post.post_type or ""),
        str(post.likes or 0),
        str(post.shares or 0),
        str(post.comments or 0),
        str(post.clicks or 0),
        str(post.impressions or 0),
        str(post.engagement_rate or 0.0),
        str(post.positive_responses or 0),
        str(post.negative_responses or 0),
        str(post.question_responses or 0),
        str(post.sentiment_summary or ""),
        str(post.ab_variant or ""),
        str(post.ab_test_group or ""),
        str(post.status or "published"),
    ]


def _get_worksheet() -> Worksheet:
    return get_or_create_worksheet(TAB_NAME, HEADERS)


def sync_posts_to_sheet(posts: list[Engagement]) -> int:
    """Write Engagement items to the Google Sheet, upserting by ID.

    Parameters:
        posts: A list of :class:`Engagement` ORM objects.

    Returns:
        The number of rows written or updated.
    """
    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("publishing_sheet.get_worksheet_failed")
        return 0

    try:
        existing_data = ws.get_all_values()
    except gspread.exceptions.APIError:
        logger.exception("publishing_sheet.read_failed")
        return 0

    id_col = HEADERS.index("ID")
    id_to_row: dict[str, int] = {}
    for idx, row in enumerate(existing_data[1:], start=2):
        if row and len(row) > id_col and row[id_col]:
            id_to_row[row[id_col]] = idx

    batch_updates: list[dict] = []
    append_rows: list[list[str]] = []
    rows_written = 0

    for post in posts:
        row_data = _post_to_row(post)
        post_id = str(post.id)

        if post_id in id_to_row:
            sheet_row = id_to_row[post_id]
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
            "publishing_sheet.synced",
            updated=len(batch_updates),
            appended=len(append_rows),
        )
    except gspread.exceptions.APIError:
        logger.exception("publishing_sheet.write_failed")
        return 0

    return rows_written


def update_metrics(row: int, metrics: dict[str, int | float | str]) -> bool:
    """Update metric cells for a specific sheet row.

    This is used by the analytics agent to push fresh engagement numbers
    without rewriting the entire sheet.

    Parameters:
        row:     The 1-based sheet row number (header is row 1, first data
                 row is 2).
        metrics: A dict whose keys are header names (e.g. ``"Likes"``,
                 ``"Engagement Rate"``) and values are the new metric values.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    # Build a map from header name to 1-based column index.
    header_to_col: dict[str, int] = {h: i + 1 for i, h in enumerate(HEADERS)}

    try:
        ws = _get_worksheet()
    except Exception:
        logger.exception("publishing_sheet.get_worksheet_failed")
        return False

    cells_to_update: list[gspread.Cell] = []
    for key, value in metrics.items():
        col = header_to_col.get(key)
        if col is None:
            logger.warning(
                "publishing_sheet.unknown_metric_column",
                key=key,
            )
            continue
        cells_to_update.append(gspread.Cell(row=row, col=col, value=str(value)))

    if not cells_to_update:
        logger.warning("publishing_sheet.no_valid_metrics", row=row)
        return False

    try:
        ws.update_cells(cells_to_update, value_input_option="USER_ENTERED")
        logger.info(
            "publishing_sheet.metrics_updated",
            row=row,
            metrics_count=len(cells_to_update),
        )
        return True
    except gspread.exceptions.APIError:
        logger.exception(
            "publishing_sheet.metrics_update_failed",
            row=row,
        )
        return False
