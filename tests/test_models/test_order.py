import pytest
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from decimal import Decimal


@pytest.mark.unit
def test_create_order(db: Session, test_user: User):
    """Test creating an order"""
    order = Order(
        user_id=test_user.id,
        order_number="ORD-TEST-001",
        status=OrderStatus.PENDING,
        subtotal=Decimal("100.00"),
        tax=Decimal("10.00"),
        shipping_cost=Decimal("5.00"),
        total=Decimal("115.00"),
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    assert order.id is not None
    assert order.order_number == "ORD-TEST-001"
    assert order.status == OrderStatus.PENDING
    assert order.total == Decimal("115.00")


@pytest.mark.unit
def test_order_with_items(db: Session, test_user: User):
    """Test order with order items"""
    product = Product(
        name="Test Product",
        slug="test-product",
        price=Decimal("50.00"),
        sku="TEST-001",
        is_active=True,
    )
    db.add(product)
    db.flush()

    order = Order(
        user_id=test_user.id,
        order_number="ORD-TEST-002",
        status=OrderStatus.PENDING,
        subtotal=Decimal("100.00"),
        tax=Decimal("10.00"),
        shipping_cost=Decimal("5.00"),
        total=Decimal("115.00"),
    )
    db.add(order)
    db.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        price=Decimal("50.00"),
        subtotal=Decimal("100.00"),
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)

    assert len(order.order_items) == 1
    assert order.order_items[0].quantity == 2
    assert order.order_items[0].subtotal == Decimal("100.00")
