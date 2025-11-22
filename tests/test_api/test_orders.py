import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.user import User
from decimal import Decimal


@pytest.mark.integration
def test_create_order_authenticated(client: TestClient, db: Session, auth_headers: dict):
    """Test creating an order as authenticated user"""
    product = Product(
        name="Order Product",
        slug="order-product",
        price=Decimal("99.99"),
        sku="ORD-001",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.post(
        "/api/v1/orders/",
        json={
            "items": [
                {
                    "product_id": str(product.id),
                    "quantity": 1,
                    "price": 99.99,
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["order_items"]) == 1


@pytest.mark.integration
def test_list_user_orders(client: TestClient, auth_headers: dict):
    """Test listing user's orders"""
    response = client.get("/api/v1/orders/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_orders_require_authentication(client: TestClient):
    """Test orders require authentication"""
    response = client.get("/api/v1/orders/")
    assert response.status_code == 401
