#!/usr/bin/env python
"""Initialize the database tables."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zipjeweler.models.database import init_db
from zipjeweler.utils.logger import get_logger, setup_logging


def main():
    setup_logging()
    logger = get_logger("setup_db")
    logger.info("Initializing database...")
    init_db()
    logger.info("Database tables created successfully")


if __name__ == "__main__":
    main()
