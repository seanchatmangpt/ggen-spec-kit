"""
specify_cli.api.billing_api - REST API for Billing & Subscriptions
==================================================================

REST API endpoints for billing operations, subscriptions, invoices, and metered usage.
Provides foundation for Freemium API monetization model.

Features:
- Subscription management endpoints
- Usage reporting endpoints
- Invoice retrieval and payment status
- SLA and support ticket endpoints
- Usage quota and rate limiting

Example Usage
-------------
    from specify_cli.api.billing_api import BillingAPIHandler

    handler = BillingAPIHandler()

    # Get subscription
    subscription = handler.get_subscription(user_id=123)

    # Track usage
    handler.track_usage(
        user_id=123,
        metric_type="api_calls",
        amount=50
    )
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from specify_cli.ops.billing import (
    InvoiceLineItem,
    SLAConfig,
    SLATier,
    SubscriptionConfig,
    SubscriptionTier,
    aggregate_usage_by_period,
    calculate_arr,
    calculate_invoice_due_date,
    calculate_invoice_line_items,
    calculate_ltv,
    calculate_mrr,
    calculate_subscription_cost,
    check_sla_compliance,
    check_usage_quota,
    get_current_billing_period,
)


@dataclass
class SubscriptionResponse:
    """Response DTO for subscription."""

    subscription_id: str
    user_id: int
    tier: str
    status: str
    start_date: str
    renewal_date: str
    monthly_cost: str
    api_quota: int
    storage_quota: int
    max_users: int
    features: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class UsageResponse:
    """Response DTO for usage data."""

    billing_period: str
    aggregated_usage: dict[str, float]
    quota_status: dict[str, Any]
    overage_charges: Decimal

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "billing_period": self.billing_period,
            "aggregated_usage": self.aggregated_usage,
            "quota_status": self.quota_status,
            "overage_charges": str(self.overage_charges),
        }


@dataclass
class InvoiceResponse:
    """Response DTO for invoice."""

    invoice_id: str
    subscription_id: str
    amount: str
    currency: str
    status: str
    billing_period_start: str
    billing_period_end: str
    issue_date: str
    due_date: str
    paid_date: str | None
    line_items: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BillingAPIHandler:
    """Handler for billing REST API endpoints.

    This handler provides business logic for REST API endpoints without
    performing any I/O operations. All data access is delegated to the
    runtime layer.
    """

    def __init__(self) -> None:
        """Initialize billing API handler."""
        pass

    # ====================================================================
    # Subscription Endpoints
    # ====================================================================

    def get_subscription(
        self,
        user_id: int,
        subscription_data: dict[str, Any] | None = None,
    ) -> SubscriptionResponse:
        """Get user's current subscription.

        Parameters
        ----------
        user_id : int
            User ID.
        subscription_data : dict
            Subscription data from database (provided by runtime layer).

        Returns
        -------
        SubscriptionResponse
            Subscription details with features and quotas.
        """
        if not subscription_data:
            subscription_data = {
                "subscription_id": "sub_unknown",
                "tier": "free",
                "status": "active",
                "start_date": datetime.now(UTC).isoformat(),
                "renewal_date": datetime.now(UTC).isoformat(),
                "monthly_cost": "0",
            }

        tier = SubscriptionTier(subscription_data.get("tier", "free"))
        config = SubscriptionConfig.get_tier_config(tier)

        return SubscriptionResponse(
            subscription_id=subscription_data.get("subscription_id", "sub_unknown"),
            user_id=user_id,
            tier=tier.value,
            status=subscription_data.get("status", "active"),
            start_date=subscription_data.get("start_date", ""),
            renewal_date=subscription_data.get("renewal_date", ""),
            monthly_cost=str(config.monthly_cost),
            api_quota=config.api_quota,
            storage_quota=config.storage_quota,
            max_users=config.max_users,
            features=config.features,
        )

    def upgrade_subscription(
        self,
        user_id: int,
        new_tier: str,
    ) -> dict[str, Any]:
        """Upgrade subscription to new tier.

        Parameters
        ----------
        user_id : int
            User ID.
        new_tier : str
            Target subscription tier.

        Returns
        -------
        dict
            Upgrade result with prorated charges if applicable.
        """
        tier = SubscriptionTier(new_tier)
        config = SubscriptionConfig.get_tier_config(tier)

        return {
            "user_id": user_id,
            "new_tier": tier.value,
            "monthly_cost": str(config.monthly_cost),
            "effective_date": datetime.now(UTC).isoformat(),
            "action": "upgrade_subscription",
            "requires_payment_method": config.monthly_cost > 0,
        }

    def downgrade_subscription(
        self,
        user_id: int,
        new_tier: str,
    ) -> dict[str, Any]:
        """Downgrade subscription to lower tier.

        Parameters
        ----------
        user_id : int
            User ID.
        new_tier : str
            Target subscription tier.

        Returns
        -------
        dict
            Downgrade result with refund if applicable.
        """
        tier = SubscriptionTier(new_tier)
        config = SubscriptionConfig.get_tier_config(tier)

        return {
            "user_id": user_id,
            "new_tier": tier.value,
            "monthly_cost": str(config.monthly_cost),
            "effective_date": datetime.now(UTC).isoformat(),
            "action": "downgrade_subscription",
        }

    def cancel_subscription(self, user_id: int) -> dict[str, Any]:
        """Cancel subscription.

        Parameters
        ----------
        user_id : int
            User ID.

        Returns
        -------
        dict
            Cancellation result.
        """
        return {
            "user_id": user_id,
            "action": "cancel_subscription",
            "status": "cancelled",
            "effective_date": datetime.now(UTC).isoformat(),
        }

    # ====================================================================
    # Usage Tracking Endpoints
    # ====================================================================

    def track_usage(
        self,
        user_id: int,
        metric_type: str,
        amount: float,
    ) -> dict[str, Any]:
        """Track usage event for metered billing.

        Parameters
        ----------
        user_id : int
            User ID.
        metric_type : str
            Type of usage (api_calls, storage, etc).
        amount : float
            Amount consumed.

        Returns
        -------
        dict
            Usage event confirmation.
        """
        billing_period = get_current_billing_period()

        return {
            "user_id": user_id,
            "metric_type": metric_type,
            "amount": amount,
            "billing_period": billing_period,
            "timestamp": datetime.now(UTC).isoformat(),
            "action": "track_usage",
        }

    def get_usage(
        self,
        user_id: int,
        usage_events: list[dict[str, Any]] | None = None,
        subscription_data: dict[str, Any] | None = None,
    ) -> UsageResponse:
        """Get usage for current billing period with quota status.

        Parameters
        ----------
        user_id : int
            User ID.
        usage_events : list
            Usage events from database (provided by runtime layer).
        subscription_data : dict
            Subscription data from database.

        Returns
        -------
        UsageResponse
            Current usage, quota status, and overage charges.
        """
        if not usage_events:
            usage_events = []
        if not subscription_data:
            subscription_data = {"tier": "free"}

        billing_period = get_current_billing_period()
        aggregated = aggregate_usage_by_period(usage_events, billing_period)

        # Get tier config for quota
        tier = SubscriptionTier(subscription_data.get("tier", "free"))
        config = SubscriptionConfig.get_tier_config(tier)

        # Check API quota
        api_calls_used = aggregated.get("api_calls", 0)
        quota_status = check_usage_quota(
            current_usage=int(api_calls_used),
            quota=config.api_quota,
        )

        # Calculate overage charges
        overage_charges = Decimal("0")
        if quota_status["is_exceeded"]:
            overage = int(api_calls_used) - config.api_quota
            overage_charges = Decimal(str(overage)) * Decimal("0.05")

        return UsageResponse(
            billing_period=billing_period,
            aggregated_usage=aggregated,
            quota_status=quota_status,
            overage_charges=overage_charges,
        )

    # ====================================================================
    # Invoice Endpoints
    # ====================================================================

    def get_invoices(
        self,
        user_id: int,
        invoices_data: list[dict[str, Any]] | None = None,
    ) -> list[InvoiceResponse]:
        """Get user's invoices.

        Parameters
        ----------
        user_id : int
            User ID.
        invoices_data : list
            Invoice records from database (provided by runtime layer).

        Returns
        -------
        list
            List of invoices.
        """
        if not invoices_data:
            invoices_data = []

        result = []
        for invoice in invoices_data:
            result.append(
                InvoiceResponse(
                    invoice_id=invoice.get("invoice_id", ""),
                    subscription_id=invoice.get("subscription_id", ""),
                    amount=str(invoice.get("amount", 0)),
                    currency=invoice.get("currency", "USD"),
                    status=invoice.get("status", "draft"),
                    billing_period_start=invoice.get("billing_period_start", ""),
                    billing_period_end=invoice.get("billing_period_end", ""),
                    issue_date=invoice.get("issue_date", ""),
                    due_date=invoice.get("due_date", ""),
                    paid_date=invoice.get("paid_date"),
                    line_items=invoice.get("line_items", {}),
                )
            )

        return result

    def generate_invoice(
        self,
        subscription_id: int,
        user_id: int,
        subscription_data: dict[str, Any],
        usage_events: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Generate invoice for subscription.

        Parameters
        ----------
        subscription_id : int
            Subscription ID.
        user_id : int
            User ID.
        subscription_data : dict
            Subscription data.
        usage_events : list
            Usage events for overage calculation.

        Returns
        -------
        dict
            Generated invoice data.
        """
        if not usage_events:
            usage_events = []

        tier = SubscriptionTier(subscription_data.get("tier", "free"))
        billing_period = get_current_billing_period()

        # Get base cost
        base_cost = calculate_subscription_cost(tier, "monthly")

        # Calculate usage overage
        usage_overage = aggregate_usage_by_period(usage_events, billing_period)

        # Generate line items
        line_items, total_amount = calculate_invoice_line_items(
            tier,
            base_cost,
            usage_overage,
        )

        # Calculate due date (30 days)
        issue_date = datetime.now(UTC)
        due_date = calculate_invoice_due_date(issue_date, 30)

        line_items_dict = [item.to_dict() for item in line_items]

        return {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "amount": str(total_amount),
            "currency": "USD",
            "billing_period_start": billing_period,
            "billing_period_end": billing_period,
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
            "line_items": line_items_dict,
            "status": "draft",
            "action": "generate_invoice",
        }

    # ====================================================================
    # SLA & Support Endpoints
    # ====================================================================

    def get_sla(self, sla_tier: str) -> dict[str, Any]:
        """Get SLA configuration for tier.

        Parameters
        ----------
        sla_tier : str
            SLA tier name.

        Returns
        -------
        dict
            SLA configuration and terms.
        """
        tier = SLATier(sla_tier)
        config = SLAConfig.get_tier_config(tier)

        return {
            "tier": tier.value,
            "name": config.name,
            "initial_response_minutes": config.initial_response_minutes,
            "resolution_minutes": config.resolution_minutes,
            "availability_percent": config.availability_percent,
            "support_hours": config.support_hours,
            "max_concurrent_tickets": config.max_concurrent_tickets,
        }

    def check_ticket_sla(
        self,
        ticket_data: dict[str, Any],
        sla_tier: str = "community",
    ) -> dict[str, Any]:
        """Check SLA compliance for ticket.

        Parameters
        ----------
        ticket_data : dict
            Ticket data from database.
        sla_tier : str
            SLA tier to check against.

        Returns
        -------
        dict
            Compliance status.
        """
        tier = SLATier(sla_tier)
        sla_config = SLAConfig.get_tier_config(tier)

        created_at = datetime.fromisoformat(ticket_data.get("created_at", datetime.now(UTC).isoformat()))
        first_response_at = None
        if ticket_data.get("first_response_at"):
            first_response_at = datetime.fromisoformat(ticket_data["first_response_at"])
        resolved_at = None
        if ticket_data.get("resolved_at"):
            resolved_at = datetime.fromisoformat(ticket_data["resolved_at"])

        return check_sla_compliance(created_at, first_response_at, resolved_at, sla_config)

    # ====================================================================
    # Analytics Endpoints
    # ====================================================================

    def get_billing_metrics(
        self,
        subscriptions_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Get key billing metrics.

        Parameters
        ----------
        subscriptions_data : list
            All subscription records (provided by runtime layer).

        Returns
        -------
        dict
            Key metrics: MRR, ARR, churn rate, LTV, etc.
        """
        if not subscriptions_data:
            subscriptions_data = []

        mrr = calculate_mrr(subscriptions_data)
        arr = calculate_arr(subscriptions_data)

        return {
            "mrr": str(mrr),
            "arr": str(arr),
            "active_subscriptions": len([s for s in subscriptions_data if s.get("status") == "active"]),
            "total_subscriptions": len(subscriptions_data),
            "timestamp": datetime.now(UTC).isoformat(),
        }
