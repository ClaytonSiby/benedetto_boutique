from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List payments for current user's orders"""
    from app.models.order import Order

    # Get user's order IDs
    order_ids = [
        order.id for order in db.query(Order.id).filter(Order.user_id == current_user.id).all()
    ]

    payments = (
        db.query(Payment)
        .filter(Payment.order_id.in_(order_ids))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment by ID"""
    from app.models.order import Order

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Verify user owns the order
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new payment"""
    from app.models.order import Order

    # Verify user owns the order
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    db_payment = Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.patch("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: UUID,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update payment"""
    from app.models.order import Order

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Verify user owns the order
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment not found")

    update_data = payment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)
    return payment
