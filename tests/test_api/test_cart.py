import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.cart import Cart
from decimal import Decimal


@pytest.mark.integration
def test_get_cart_authenticated(client: TestClient, auth_headers: dict):
    """Test getting cart for authenticated user"""
    response = client.get("/api/v1/cart/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "cart_items" in data


@pytest.mark.integration
def test_add_to_cart(client: TestClient, db: Session, auth_headers: dict):
    """Test adding product to cart"""
    product = Product(
        name="Cart Product",
        slug="cart-product",
        price=Decimal("39.99"),
        sku="CART-001",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": str(product.id), "quantity": 2},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["cart_items"]) == 1
    assert data["cart_items"][0]["quantity"] == 2


@pytest.mark.integration
def test_cart_requires_authentication(client: TestClient):
    """Test cart endpoints require authentication"""
    response = client.get("/api/v1/cart/")
    assert response.status_code == 401
