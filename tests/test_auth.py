"""
Tests for POST /auth/login
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


LOGIN_URL = "/auth/login"

VALID_PAYLOAD = {
    "email": "john@example.com",
    "password": "Test@1234",
}


class TestLogin:
    def test_login_success(self, client: TestClient, mock_db: MagicMock):
        """Valid credentials return 200 and an access token."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = VALID_PAYLOAD["email"]
        mock_user.password = VALID_PAYLOAD["password"]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch("app.api.auth.issue_and_store_tokens") as mock_issue:
            mock_issue.return_value = MagicMock(access_token="fake_access_token")
            response = client.post(LOGIN_URL, json=VALID_PAYLOAD)

        assert response.status_code == 200
        assert response.json()["token"] == "fake_access_token"

    def test_login_wrong_password(self, client: TestClient, mock_db: MagicMock):
        """Correct email but wrong password returns 401."""
        mock_user = MagicMock()
        mock_user.email = VALID_PAYLOAD["email"]
        mock_user.password = "Correct@9999"  # stored password differs
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        response = client.post(LOGIN_URL, json=VALID_PAYLOAD)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_user_not_found(self, client: TestClient, mock_db: MagicMock):
        """Non-existent email returns 401."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.post(LOGIN_URL, json=VALID_PAYLOAD)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
