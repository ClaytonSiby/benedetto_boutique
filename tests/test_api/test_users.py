import pytest
from fastapi.testclient import TestClient
from app.models.user import User


@pytest.mark.integration
def test_get_current_user(client: TestClient, auth_headers: dict, test_user: User):
    """Test getting current user info"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.integration
def test_users_require_authentication(client: TestClient):
    """Test users endpoints require authentication"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
