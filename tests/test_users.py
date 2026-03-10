"""
Tests for POST /users (user registration)
"""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


USERS_URL = "/users"

VALID_PAYLOAD = {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "Test@1234",
    "phone": "1234567890",
    "date_of_birth": "1990-01-01",
    "role_id": 1,
}


class TestCreateUser:
    def test_create_user_success(self, client: TestClient, mock_db: MagicMock):
        """Valid payload creates a user and returns 201 with a token."""
        # No existing user with that email
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_new_user = MagicMock()
        mock_new_user.id = 1
        mock_new_user.name = "John Doe"
        mock_new_user.email = "john@example.com"
        mock_new_user.date_of_birth = date(1990, 1, 1)
        mock_new_user.phone = "1234567890"
        mock_new_user.website = None
        mock_new_user.profile_image = None
        mock_new_user.role = None

        with patch("app.api.routers.users.User", return_value=mock_new_user), \
             patch("app.api.routers.users.issue_and_store_tokens") as mock_issue:
            mock_issue.return_value = MagicMock(access_token="new_user_token")
            response = client.post(USERS_URL, json=VALID_PAYLOAD)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "john@example.com"
        assert data["token"] == "new_user_token"

    def test_create_user_duplicate_email(self, client: TestClient, mock_db: MagicMock):
        """Registration with an already-taken email returns 409."""
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

        response = client.post(USERS_URL, json=VALID_PAYLOAD)

        assert response.status_code == 409
        assert "Email already exists" in response.json()["detail"]

    def test_create_user_invalid_role(self, client: TestClient, mock_db: MagicMock):
        """Unsupported role_id value returns 400."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        payload = {**VALID_PAYLOAD, "role_id": 99}
        response = client.post(USERS_URL, json=payload)

        assert response.status_code == 400
        assert "Invalid role" in response.json()["detail"]

    def test_create_user_weak_password_rejected(self, client: TestClient):
        """Password that fails Pydantic validation returns 422."""
        payload = {**VALID_PAYLOAD, "password": "weak"}
        response = client.post(USERS_URL, json=payload)

        assert response.status_code == 422
