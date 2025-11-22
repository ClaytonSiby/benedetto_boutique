import pytest
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.category import Category
from decimal import Decimal


@pytest.mark.unit
def test_create_product(db: Session):
    """Test creating a product"""
    product = Product(
        name="Test Product",
        slug="test-product",
        description="A test product",
        price=Decimal("99.99"),
        sku="TEST-001",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    assert product.id is not None
    assert product.name == "Test Product"
    assert product.price == Decimal("99.99")
    assert product.sku == "TEST-001"


@pytest.mark.unit
def test_product_with_category(db: Session):
    """Test product with category relationship"""
    category = Category(
        name="Electronics",
        slug="electronics",
        is_active=True,
    )
    db.add(category)
    db.flush()

    product = Product(
        name="Laptop",
        slug="laptop",
        price=Decimal("999.99"),
        sku="LAP-001",
        category_id=category.id,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    assert product.category is not None
    assert product.category.name == "Electronics"


@pytest.mark.unit
def test_product_sale_price(db: Session):
    """Test product with sale price"""
    product = Product(
        name="Sale Item",
        slug="sale-item",
        price=Decimal("100.00"),
        sale_price=Decimal("79.99"),
        sku="SALE-001",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    assert product.sale_price == Decimal("79.99")
    assert product.sale_price < product.price
