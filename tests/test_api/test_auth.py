import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_login_success(client: TestClient, test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
def test_login_invalid_credentials(client: TestClient, test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nonexistent", "password": "password"},
    )
    assert response.status_code == 401
