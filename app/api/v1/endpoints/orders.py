from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal
import uuid

from app.db.session import get_db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's orders"""
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get order by ID"""
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new order"""
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in order_data.items)
    tax = subtotal * Decimal("0.1")  # 10% tax
    shipping_cost = Decimal("10.00")  # Fixed shipping
    total = subtotal + tax + shipping_cost

    # Generate order number
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # Create order
    db_order = Order(
        user_id=current_user.id,
        order_number=order_number,
        subtotal=subtotal,
        tax=tax,
        shipping_cost=shipping_cost,
        total=total,
        shipping_address_id=order_data.shipping_address_id,
        billing_address_id=order_data.billing_address_id,
    )
    db.add(db_order)
    db.flush()

    # Create order items
    for item in order_data.items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
            subtotal=item.price * item.quantity,
        )
        db.add(order_item)

    db.commit()
    db.refresh(db_order)
    return db_order


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: UUID,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update order"""
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete order"""
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return None
