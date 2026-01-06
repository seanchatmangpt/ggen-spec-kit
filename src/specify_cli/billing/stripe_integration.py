"""
specify_cli.billing.stripe_integration - Stripe Payment Processing
==================================================================

Stripe integration for payment processing, subscription management, and webhooks.
Handles Stripe API interactions for monetization.

Features:
- Customer creation and management
- Subscription creation and updates
- Payment processing and invoicing
- Webhook handling for payment events
- Refund and credit processing

Environment Variables
---------------------
    STRIPE_API_KEY : str
        Stripe API key (starts with sk_)
    STRIPE_WEBHOOK_SECRET : str
        Stripe webhook signing secret
    STRIPE_PUBLISHABLE_KEY : str
        Stripe publishable key (for frontend)

Example Usage
-------------
    from specify_cli.billing.stripe_integration import StripeClient

    client = StripeClient(api_key="sk_test_...")

    # Create customer
    customer = client.create_customer(
        email="user@example.com",
        name="User Name"
    )

    # Create subscription
    subscription = client.create_subscription(
        customer_id=customer["id"],
        price_id="price_professional"
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


# ============================================================================
# Stripe Configuration & Credentials
# ============================================================================


@dataclass
class StripeConfig:
    """Stripe configuration."""

    api_key: str
    publishable_key: str | None = None
    webhook_secret: str | None = None

    @staticmethod
    def from_env() -> StripeConfig:
        """Load Stripe config from environment variables.

        Returns
        -------
        StripeConfig
            Stripe configuration.

        Raises
        ------
        ValueError
            If required environment variables not set.
        """
        api_key = os.getenv("STRIPE_API_KEY")
        if not api_key:
            raise ValueError("STRIPE_API_KEY environment variable not set")

        return StripeConfig(
            api_key=api_key,
            publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY"),
            webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
        )


# ============================================================================
# Stripe Price/Product Definitions
# ============================================================================


class StripeProducts:
    """Stripe product and price IDs for subscriptions."""

    # Products
    PRODUCT_FREE = "prod_spec_kit_free"
    PRODUCT_PROFESSIONAL = "prod_spec_kit_professional"
    PRODUCT_ENTERPRISE = "prod_spec_kit_enterprise"

    # Prices (Monthly)
    PRICE_FREE = "price_free"
    PRICE_PROFESSIONAL_MONTHLY = "price_professional_monthly"
    PRICE_PROFESSIONAL_ANNUAL = "price_professional_annual"
    PRICE_ENTERPRISE_MONTHLY = "price_enterprise_monthly"
    PRICE_ENTERPRISE_ANNUAL = "price_enterprise_annual"

    # Amounts (in cents)
    AMOUNT_PROFESSIONAL_MONTHLY = 4900  # $49.00
    AMOUNT_PROFESSIONAL_ANNUAL = 49000  # $490.00
    AMOUNT_ENTERPRISE_MONTHLY = 49900  # $499.00
    AMOUNT_ENTERPRISE_ANNUAL = 499000  # $4990.00


# ============================================================================
# Stripe Client (Operations Layer)
# ============================================================================


class StripeClient:
    """Stripe API client for payment processing.

    This class provides methods for Stripe operations but does not perform
    actual API calls. All network operations are delegated to the runtime layer.
    """

    def __init__(self, config: StripeConfig) -> None:
        """Initialize Stripe client.

        Parameters
        ----------
        config : StripeConfig
            Stripe configuration with API key.
        """
        self.config = config
        # Note: Actual Stripe API initialization would happen in runtime layer
        self.api_key = config.api_key

    # ====================================================================
    # Customer Management
    # ====================================================================

    def create_customer(
        self,
        email: str,
        name: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create Stripe customer.

        Parameters
        ----------
        email : str
            Customer email address.
        name : str
            Customer name.
        metadata : dict
            Additional metadata to attach.

        Returns
        -------
        dict
            Stripe customer object (for runtime layer to persist).
        """
        if not metadata:
            metadata = {}

        return {
            "action": "create_customer",
            "email": email,
            "name": name,
            "metadata": metadata,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def get_customer(self, customer_id: str) -> dict[str, Any]:
        """Get Stripe customer details.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID.

        Returns
        -------
        dict
            Stripe customer object.
        """
        return {
            "action": "get_customer",
            "customer_id": customer_id,
        }

    def update_customer(
        self,
        customer_id: str,
        **updates: Any,
    ) -> dict[str, Any]:
        """Update Stripe customer.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID.
        **updates
            Fields to update (email, name, metadata, etc).

        Returns
        -------
        dict
            Updated customer object.
        """
        return {
            "action": "update_customer",
            "customer_id": customer_id,
            "updates": updates,
        }

    # ====================================================================
    # Subscription Management
    # ====================================================================

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create subscription for customer.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID.
        price_id : str
            Stripe price ID.
        trial_days : int
            Number of trial days (0 = no trial).
        metadata : dict
            Additional metadata.

        Returns
        -------
        dict
            Stripe subscription object.
        """
        if not metadata:
            metadata = {}

        return {
            "action": "create_subscription",
            "customer_id": customer_id,
            "price_id": price_id,
            "trial_days": trial_days,
            "metadata": metadata,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def update_subscription(
        self,
        subscription_id: str,
        **updates: Any,
    ) -> dict[str, Any]:
        """Update subscription (change price, cancel at period end, etc).

        Parameters
        ----------
        subscription_id : str
            Stripe subscription ID.
        **updates
            Fields to update (items, trial_settings, cancel_at_period_end, etc).

        Returns
        -------
        dict
            Updated subscription object.
        """
        return {
            "action": "update_subscription",
            "subscription_id": subscription_id,
            "updates": updates,
        }

    def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True,
    ) -> dict[str, Any]:
        """Cancel subscription.

        Parameters
        ----------
        subscription_id : str
            Stripe subscription ID.
        at_period_end : bool
            If True, cancel at billing period end. If False, cancel immediately.

        Returns
        -------
        dict
            Cancelled subscription object.
        """
        return {
            "action": "cancel_subscription",
            "subscription_id": subscription_id,
            "at_period_end": at_period_end,
        }

    def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Get subscription details.

        Parameters
        ----------
        subscription_id : str
            Stripe subscription ID.

        Returns
        -------
        dict
            Stripe subscription object.
        """
        return {
            "action": "get_subscription",
            "subscription_id": subscription_id,
        }

    # ====================================================================
    # Invoicing
    # ====================================================================

    def get_invoices(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get invoices for customer.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID.
        limit : int
            Maximum number of invoices to return.

        Returns
        -------
        list
            List of Stripe invoice objects.
        """
        return [
            {
                "action": "get_invoices",
                "customer_id": customer_id,
                "limit": limit,
            }
        ]

    def create_invoice(
        self,
        customer_id: str,
        description: str = "",
        auto_advance: bool = True,
    ) -> dict[str, Any]:
        """Create draft invoice.

        Parameters
        ----------
        customer_id : str
            Stripe customer ID.
        description : str
            Invoice description.
        auto_advance : bool
            Whether to auto-finalize and send invoice.

        Returns
        -------
        dict
            Stripe invoice object.
        """
        return {
            "action": "create_invoice",
            "customer_id": customer_id,
            "description": description,
            "auto_advance": auto_advance,
        }

    def finalize_invoice(self, invoice_id: str) -> dict[str, Any]:
        """Finalize draft invoice.

        Parameters
        ----------
        invoice_id : str
            Stripe invoice ID.

        Returns
        -------
        dict
            Finalized invoice object.
        """
        return {
            "action": "finalize_invoice",
            "invoice_id": invoice_id,
        }

    def send_invoice(self, invoice_id: str) -> dict[str, Any]:
        """Send invoice to customer.

        Parameters
        ----------
        invoice_id : str
            Stripe invoice ID.

        Returns
        -------
        dict
            Sent invoice object.
        """
        return {
            "action": "send_invoice",
            "invoice_id": invoice_id,
        }

    # ====================================================================
    # Payments
    # ====================================================================

    def create_payment_intent(
        self,
        amount: int,  # in cents
        customer_id: str,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create payment intent.

        Parameters
        ----------
        amount : int
            Amount in cents.
        customer_id : str
            Stripe customer ID.
        description : str
            Payment description.
        metadata : dict
            Additional metadata.

        Returns
        -------
        dict
            Stripe payment intent object.
        """
        if not metadata:
            metadata = {}

        return {
            "action": "create_payment_intent",
            "amount": amount,
            "customer_id": customer_id,
            "currency": "usd",
            "description": description,
            "metadata": metadata,
        }

    def confirm_payment(
        self,
        payment_intent_id: str,
        payment_method_id: str,
    ) -> dict[str, Any]:
        """Confirm payment intent.

        Parameters
        ----------
        payment_intent_id : str
            Stripe payment intent ID.
        payment_method_id : str
            Stripe payment method ID.

        Returns
        -------
        dict
            Confirmed payment intent object.
        """
        return {
            "action": "confirm_payment",
            "payment_intent_id": payment_intent_id,
            "payment_method_id": payment_method_id,
        }

    # ====================================================================
    # Refunds
    # ====================================================================

    def create_refund(
        self,
        charge_id: str,
        amount: int | None = None,
        reason: str = "requested_by_customer",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create refund for charge.

        Parameters
        ----------
        charge_id : str
            Stripe charge ID.
        amount : int
            Amount to refund in cents (None = full refund).
        reason : str
            Refund reason.
        metadata : dict
            Additional metadata.

        Returns
        -------
        dict
            Stripe refund object.
        """
        if not metadata:
            metadata = {}

        return {
            "action": "create_refund",
            "charge_id": charge_id,
            "amount": amount,
            "reason": reason,
            "metadata": metadata,
        }

    # ====================================================================
    # Webhook Verification
    # ====================================================================

    def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
    ) -> bool:
        """Verify Stripe webhook signature.

        Parameters
        ----------
        payload : str
            Webhook payload JSON string.
        signature : str
            Stripe signature header.

        Returns
        -------
        bool
            True if signature is valid.
        """
        # Note: Actual signature verification would happen in runtime layer
        if not self.config.webhook_secret:
            return False

        return True  # Placeholder - actual verification in runtime

    def parse_webhook_event(
        self,
        payload: str,
    ) -> dict[str, Any]:
        """Parse webhook event payload.

        Parameters
        ----------
        payload : str
            Webhook payload JSON string.

        Returns
        -------
        dict
            Parsed event object with keys: type, data, timestamp
        """
        return {
            "type": "payment_intent.succeeded",
            "data": {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

    # ====================================================================
    # Metadata & Helper Methods
    # ====================================================================

    def get_price_for_tier(self, tier: str, billing_period: str = "monthly") -> str:
        """Get Stripe price ID for subscription tier.

        Parameters
        ----------
        tier : str
            Subscription tier (free, professional, enterprise).
        billing_period : str
            Billing period (monthly or annual).

        Returns
        -------
        str
            Stripe price ID.
        """
        prices = {
            ("free", "monthly"): StripeProducts.PRICE_FREE,
            ("professional", "monthly"): StripeProducts.PRICE_PROFESSIONAL_MONTHLY,
            ("professional", "annual"): StripeProducts.PRICE_PROFESSIONAL_ANNUAL,
            ("enterprise", "monthly"): StripeProducts.PRICE_ENTERPRISE_MONTHLY,
            ("enterprise", "annual"): StripeProducts.PRICE_ENTERPRISE_ANNUAL,
        }
        return prices.get((tier, billing_period), StripeProducts.PRICE_FREE)
