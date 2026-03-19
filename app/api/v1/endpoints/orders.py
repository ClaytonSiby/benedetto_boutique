from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from decimal import Decimal
import uuid

from app.db.session import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/stats", tags=["orders"])
def order_stats(db: Session = Depends(get_db)):
    """Get order statistics including status breakdown and recent orders"""
    from sqlalchemy import func

    total = db.query(Order).count()
    total_revenue = db.query(func.coalesce(func.sum(Order.total), 0)).scalar()

    # Status breakdown
    status_rows = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    status_breakdown = {status.value: count for status, count in status_rows}

    # Recent 5 orders with user email
    recent_rows = (
        db.query(Order, User.email)
        .outerjoin(User, Order.user_id == User.id)
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )
    recent_orders = [
        {
            "id": str(order.id),
            "order_number": order.order_number,
            "user_email": email or "Guest",
            "total": float(order.total),
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
        }
        for order, email in recent_rows
    ]

    return {
        "total": total,
        "total_revenue": float(total_revenue),
        "status_breakdown": status_breakdown,
        "recent_orders": recent_orders,
    }


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
    """Get order by ID with all related data"""
    order = (
        db.query(Order)
        .options(
            joinedload(Order.order_items).joinedload(OrderItem.product),
            joinedload(Order.payment)
        )
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

    # Create payment record
    payment = Payment(
        order_id=db_order.id,
        payment_method=order_data.payment_method or "card",
        amount=total,
        currency="ZAR",
        status=PaymentStatus.PENDING,
    )
    db.add(payment)

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


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an order"""
    order = (
        db.query(Order)
        .options(joinedload(Order.payment))
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if order can be cancelled
    if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status: {order.status}"
        )

    # Update order status
    order.status = OrderStatus.CANCELLED

    # If payment exists and is completed, mark it for refund
    if order.payment and order.payment.status == PaymentStatus.COMPLETED:
        order.payment.status = PaymentStatus.REFUNDED
        # In production, you would initiate an actual refund via Stripe here
        # stripe.refund.create(payment_intent=order.payment.transaction_id)

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
