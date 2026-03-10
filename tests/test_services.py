"""
Tests for POST /services (service creation)
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


SERVICES_URL = "/services"

VALID_PAYLOAD = {
    "name": "Home Cleaning",
    "description": "Professional home cleaning service",
    "price": 150,
    "status": True,
}


class TestCreateService:
    def test_create_service_as_provider(self, provider_client: TestClient, mock_db: MagicMock):
        """A provider (role_id=2) can create a service and receives 201."""
        mock_new_service = MagicMock()
        mock_new_service.id = 1
        mock_new_service.name = VALID_PAYLOAD["name"]
        mock_new_service.description = VALID_PAYLOAD["description"]
        mock_new_service.price = VALID_PAYLOAD["price"]
        mock_new_service.status = VALID_PAYLOAD["status"]
        # provider attribute mirrors the authenticated mock user
        mock_new_service.provider.id = 2
        mock_new_service.provider.name = "Test User"
        mock_new_service.provider.email = "provider@example.com"

        with patch("app.api.routers.services.Service", return_value=mock_new_service), \
             patch("app.api.routers.services.cache_manager"):
            response = provider_client.post(SERVICES_URL, json=VALID_PAYLOAD)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == VALID_PAYLOAD["name"]
        assert data["price"] == VALID_PAYLOAD["price"]

    def test_create_service_as_regular_user_forbidden(self, user_client: TestClient):
        """A regular user (role_id=1) attempting to create a service gets 403."""
        response = user_client.post(SERVICES_URL, json=VALID_PAYLOAD)

        assert response.status_code == 403
        assert "Only providers can create services" in response.json()["detail"]

    def test_create_service_invalid_price(self, provider_client: TestClient):
        """A price of 0 fails Pydantic validation and returns 422."""
        payload = {**VALID_PAYLOAD, "price": 0}
        response = provider_client.post(SERVICES_URL, json=payload)

        assert response.status_code == 422
