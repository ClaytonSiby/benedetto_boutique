from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import stripe
import os

from app.db.session import get_db
from app.models.payment import Payment, PaymentStatus
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.api.deps import get_current_user

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


@router.post("/create-payment-intent")
async def create_payment_intent(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe PaymentIntent for an order"""
    # Verify order belongs to user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(float(order.total) * 100),  # Convert to cents
            currency="zar",  # South African Rand
            metadata={
                "order_id": str(order.id),
                "order_number": order.order_number,
                "user_id": str(current_user.id),
            },
        )

        return {
            "clientSecret": intent.client_secret,
            "paymentIntentId": intent.id,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: dict,
    db: Session = Depends(get_db),
):
    """Handle Stripe webhook events"""
    event_type = request.get("type")
    data = request.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        payment_intent_id = data.get("id")
        metadata = data.get("metadata", {})
        order_id = metadata.get("order_id")

        if order_id:
            # Update order and create payment record
            order = db.query(Order).filter(Order.id == UUID(order_id)).first()
            if order:
                # Create payment record
                payment = Payment(
                    order_id=order.id,
                    payment_method="stripe",
                    amount=order.total,
                    currency="zar",
                    status=PaymentStatus.COMPLETED,
                    transaction_id=payment_intent_id,
                    provider_data=metadata,
                )
                db.add(payment)

                # Update order status
                order.status = "processing"

                db.commit()

    return {"status": "success"}


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List payments for current user's orders"""

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


@router.post("/create-intent")
async def create_payment_intent_for_order(
    order_id: UUID,
    payment_method: str,
    amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a payment intent for an order"""

    # Verify order belongs to user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if payment already exists for this order
    existing_payment = db.query(Payment).filter(
        Payment.order_id == order_id,
        Payment.status == PaymentStatus.COMPLETED
    ).first()

    if existing_payment:
        raise HTTPException(status_code=400, detail="Order already paid")

    # Create payment record
    payment = Payment(
        order_id=order_id,
        payment_method=payment_method,
        amount=str(amount),
        currency="zar",
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "id": str(payment.id),
        "amount": amount,
        "currency": "zar",
        "status": "pending"
    }


@router.post("/{payment_id}/confirm")
async def confirm_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm a payment as completed""", OrderStatus

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Verify user owns the order
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Update payment status
    payment.status = PaymentStatus.COMPLETED

    # Update order status to PROCESSING
    order.status = OrderStatus.PROCESSING

    db.commit()
    db.refresh(payment)

    return {
        "id": str(payment.id),
        "status": "completed",
        "order_id": str(order.id)
    }
