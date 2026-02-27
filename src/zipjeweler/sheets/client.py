"""Google Sheets client — authenticated access via gspread + service account."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import gspread
import structlog
from google.oauth2.service_account import Credentials

from zipjeweler.config.settings import get_settings

if TYPE_CHECKING:
    from gspread import Client, Spreadsheet, Worksheet

logger = structlog.get_logger(__name__)

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Module-level cache so we reuse a single client per process.
_lock = threading.Lock()
_cached_client: Client | None = None


def get_client() -> Client:
    """Return an authenticated gspread Client (cached per-process).

    Uses the Google service-account JSON file whose path is stored in
    ``settings.google_service_account_file``.

    Raises:
        FileNotFoundError: If the service-account file cannot be found.
        google.auth.exceptions.DefaultCredentialsError: On invalid credentials.
    """
    global _cached_client

    with _lock:
        if _cached_client is not None:
            return _cached_client

        settings = get_settings()
        sa_path = settings.google_service_account_file

        logger.info("sheets.client.authenticating", service_account_file=sa_path)

        try:
            credentials = Credentials.from_service_account_file(
                sa_path,
                scopes=_SCOPES,
            )
            _cached_client = gspread.authorize(credentials)
            logger.info("sheets.client.authenticated")
            return _cached_client
        except FileNotFoundError:
            logger.error(
                "sheets.client.service_account_file_not_found",
                path=sa_path,
            )
            raise
        except Exception:
            logger.exception("sheets.client.auth_failed")
            raise


def get_spreadsheet() -> Spreadsheet:
    """Open the project spreadsheet by its ID (from settings).

    Returns:
        A :class:`gspread.Spreadsheet` handle.

    Raises:
        gspread.exceptions.SpreadsheetNotFound: If the ID is invalid or not
            shared with the service account.
    """
    settings = get_settings()
    spreadsheet_id = settings.google_spreadsheet_id

    if not spreadsheet_id:
        raise ValueError(
            "google_spreadsheet_id is not configured. "
            "Set GOOGLE_SPREADSHEET_ID in your .env file."
        )

    client = get_client()

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        logger.info(
            "sheets.client.spreadsheet_opened",
            title=spreadsheet.title,
            spreadsheet_id=spreadsheet_id,
        )
        return spreadsheet
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(
            "sheets.client.spreadsheet_not_found",
            spreadsheet_id=spreadsheet_id,
        )
        raise
    except gspread.exceptions.APIError as exc:
        logger.error(
            "sheets.client.api_error",
            spreadsheet_id=spreadsheet_id,
            error=str(exc),
        )
        raise


def get_or_create_worksheet(
    name: str,
    headers: list[str],
    rows: int = 1000,
    cols: int | None = None,
) -> Worksheet:
    """Return the worksheet *name*, creating it (with *headers*) if absent.

    Parameters:
        name:    Tab / worksheet title, e.g. ``"Intelligence -- Daily Brief"``.
        headers: Column headers to write into row 1 when creating the sheet.
        rows:    Default row count for a new worksheet.
        cols:    Default column count; defaults to ``len(headers)``.

    Returns:
        A :class:`gspread.Worksheet` handle.
    """
    if cols is None:
        cols = len(headers)

    spreadsheet = get_spreadsheet()

    try:
        worksheet = spreadsheet.worksheet(name)
        logger.debug("sheets.client.worksheet_found", name=name)
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        logger.info("sheets.client.creating_worksheet", name=name, headers=headers)

    # Worksheet does not exist yet -- create it.
    try:
        worksheet = spreadsheet.add_worksheet(title=name, rows=rows, cols=cols)
        # Write header row.
        if headers:
            worksheet.update(range_name="A1", values=[headers])
            worksheet.format(
                "A1:{}1".format(gspread.utils.rowcol_to_a1(1, cols).replace("1", "")),
                {"textFormat": {"bold": True}},
            )
        logger.info("sheets.client.worksheet_created", name=name)
        return worksheet
    except gspread.exceptions.APIError as exc:
        logger.error(
            "sheets.client.create_worksheet_failed",
            name=name,
            error=str(exc),
        )
        raise
