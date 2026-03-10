import os

# Must be set before app imports so create_engine() doesn't fail if .env is absent
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost/testdb")

import pytest
from datetime import date
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db
from app.core.security import get_current_user


def make_mock_user(role_id: int = 1, user_id: int = 1, email: str = "test@example.com") -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.name = "Test User"
    user.email = email
    user.date_of_birth = date(1990, 1, 1)
    user.phone = "1234567890"
    user.website = None
    user.profile_image = None
    user.role_id = role_id
    user.role = MagicMock()
    user.role.id = role_id
    user.role.name = "user" if role_id == 1 else "provider"
    user.personal_access_tokens = []
    return user


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(mock_db: MagicMock):
    """Unauthenticated test client with a mocked DB session."""
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        with patch("app.main.init_db"):
            with TestClient(app) as c:
                yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def user_client(mock_db: MagicMock):
    """Client pre-authenticated as a regular user (role_id=1)."""
    mock_user = make_mock_user(role_id=1)
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    try:
        with patch("app.main.init_db"):
            with TestClient(app) as c:
                yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def provider_client(mock_db: MagicMock):
    """Client pre-authenticated as a provider (role_id=2)."""
    mock_user = make_mock_user(role_id=2, user_id=2, email="provider@example.com")
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    try:
        with patch("app.main.init_db"):
            with TestClient(app) as c:
                yield c
    finally:
        app.dependency_overrides.clear()
