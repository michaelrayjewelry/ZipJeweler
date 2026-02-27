"""Shared test fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Set minimal environment variables for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("DRY_RUN", "true")
    monkeypatch.setenv("HUMAN_APPROVAL_REQUIRED", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")


@pytest.fixture
def db_session(mock_env):
    """Create an in-memory database session for testing."""
    from zipjeweler.models.database import Base, get_engine

    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import sessionmaker

    session = sessionmaker(bind=engine)()
    yield session
    session.close()
