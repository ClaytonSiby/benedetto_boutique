"""Stripe payment service for handling payments and webhooks."""

import stripe
from typing import Dict, Any, Optional
from decimal import Decimal
from uuid import UUID

from app.core.config import settings

# Initialize Stripe with secret key
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe payment operations."""

    @staticmethod
    def create_payment_intent(
        amount: Decimal,
        currency: str = "zar",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent.

        Args:
            amount: Amount in currency (e.g., 100.50 for R100.50)
            currency: Currency code (default: zar for South African Rand)
            metadata: Additional metadata to attach to the payment

        Returns:
            Dict containing payment intent details including client_secret
        """
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key is not configured")

        # Stripe expects amount in cents (smallest currency unit)
        amount_cents = int(amount * 100)

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )

            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": payment_intent.status,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a Stripe Payment Intent by ID.

        Args:
            payment_intent_id: The Stripe Payment Intent ID

        Returns:
            Dict containing payment intent details
        """
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key is not configured")

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                "id": payment_intent.id,
                "amount": Decimal(payment_intent.amount) / 100,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
                "metadata": payment_intent.metadata,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def confirm_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm a Stripe Payment Intent.

        Args:
            payment_intent_id: The Stripe Payment Intent ID

        Returns:
            Dict containing updated payment intent details
        """
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key is not configured")

        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)

            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": Decimal(payment_intent.amount) / 100,
                "currency": payment_intent.currency,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def cancel_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Cancel a Stripe Payment Intent.

        Args:
            payment_intent_id: The Stripe Payment Intent ID

        Returns:
            Dict containing cancelled payment intent details
        """
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key is not configured")

        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)

            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": Decimal(payment_intent.amount) / 100,
                "currency": payment_intent.currency,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def create_refund(
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a refund for a payment.

        Args:
            payment_intent_id: The Stripe Payment Intent ID
            amount: Optional partial refund amount (defaults to full refund)
            reason: Optional reason for refund

        Returns:
            Dict containing refund details
        """
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key is not configured")

        try:
            refund_params = {"payment_intent": payment_intent_id}

            if amount:
                refund_params["amount"] = int(amount * 100)

            if reason:
                refund_params["reason"] = reason

            refund = stripe.Refund.create(**refund_params)

            return {
                "id": refund.id,
                "amount": Decimal(refund.amount) / 100,
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> Any:
        """
        Construct and verify a Stripe webhook event.

        Args:
            payload: Raw request body bytes
            sig_header: Stripe signature header

        Returns:
            Verified Stripe event object
        """
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("Stripe webhook secret is not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            raise Exception(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {str(e)}")

    @staticmethod
    def get_publishable_key() -> str:
        """
        Get the Stripe publishable key for frontend use.

        Returns:
            Stripe publishable key
        """
        if not settings.STRIPE_PUBLISHABLE_KEY:
            raise ValueError("Stripe publishable key is not configured")
        return settings.STRIPE_PUBLISHABLE_KEY


# Create singleton instance
stripe_service = StripeService()
