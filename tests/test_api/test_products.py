import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.product import Product
from decimal import Decimal


@pytest.mark.integration
def test_list_products_public(client: TestClient, db: Session):
    """Test listing products without authentication"""
    product = Product(
        name="Public Product",
        slug="public-product",
        price=Decimal("29.99"),
        sku="PUB-001",
        is_active=True,
    )
    db.add(product)
    db.commit()

    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Public Product"


@pytest.mark.integration
def test_get_product_by_id_public(client: TestClient, db: Session):
    """Test getting product by ID without authentication"""
    product = Product(
        name="Test Product",
        slug="test-product",
        price=Decimal("49.99"),
        sku="TEST-001",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == "49.99"


@pytest.mark.integration
def test_create_product_requires_admin(client: TestClient, auth_headers: dict):
    """Test creating product requires admin role"""
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "New Product",
            "slug": "new-product",
            "price": 99.99,
            "sku": "NEW-001",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 403  # Regular user should be forbidden


@pytest.mark.integration
def test_create_product_as_admin(client: TestClient, admin_headers: dict):
    """Test creating product as admin"""
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Admin Product",
            "slug": "admin-product",
            "price": 199.99,
            "sku": "ADMIN-001",
            "is_active": True,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Admin Product"
    assert data["sku"] == "ADMIN-001"


@pytest.mark.integration
def test_update_product_as_admin(client: TestClient, db: Session, admin_headers: dict):
    """Test updating product as admin"""
    product = Product(
        name="Old Name",
        slug="old-name",
        price=Decimal("50.00"),
        sku="OLD-001",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.patch(
        f"/api/v1/products/{product.id}",
        json={"name": "New Name", "price": 75.00},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["price"] == "75.00"


@pytest.mark.integration
def test_delete_product_as_admin(client: TestClient, db: Session, admin_headers: dict):
    """Test deleting product as admin"""
    product = Product(
        name="To Delete",
        slug="to-delete",
        price=Decimal("10.00"),
        sku="DEL-001",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.delete(
        f"/api/v1/products/{product.id}", headers=admin_headers)
    assert response.status_code == 204

    # Verify deleted
    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == 404
