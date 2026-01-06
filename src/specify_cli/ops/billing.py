"""
specify_cli.ops.billing - Billing & Revenue Operations Layer
=============================================================

Pure business logic for billing, subscriptions, usage tracking, and invoicing.
This layer has no side effects - all data persistence is handled by the runtime layer.

Features:
- Subscription tier management
- Usage event tracking and aggregation
- Invoice generation and management
- Metered billing calculations
- SLA and support tier management
- Usage quota enforcement

Implements three-tier architecture:
- Commands layer: CLI interface
- Ops layer (this module): Business logic only
- Runtime layer: Database I/O, external API calls
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""

    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class InvoiceStatus(str, Enum):
    """Invoice payment status."""

    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class SLATier(str, Enum):
    """Support SLA tier levels."""

    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM_ENTERPRISE = "premium_enterprise"


# ============================================================================
# Subscription Operations
# ============================================================================


@dataclass
class SubscriptionConfig:
    """Configuration for a subscription tier."""

    tier: SubscriptionTier
    monthly_cost: Decimal
    annual_cost: Decimal
    api_quota: int  # API calls per month
    storage_quota: int  # Storage in bytes
    max_users: int
    features: dict[str, bool]

    @staticmethod
    def get_tier_config(tier: SubscriptionTier) -> SubscriptionConfig:
        """Get configuration for a subscription tier."""
        configs = {
            SubscriptionTier.FREE: SubscriptionConfig(
                tier=SubscriptionTier.FREE,
                monthly_cost=Decimal("0"),
                annual_cost=Decimal("0"),
                api_quota=100,
                storage_quota=2 * 1024 * 1024 * 1024,  # 2GB
                max_users=1,
                features={
                    "web_editor": True,
                    "api_access": False,
                    "custom_domain": False,
                    "audit_logs": False,
                    "sso": False,
                    "priority_support": False,
                    "webhooks": False,
                },
            ),
            SubscriptionTier.PROFESSIONAL: SubscriptionConfig(
                tier=SubscriptionTier.PROFESSIONAL,
                monthly_cost=Decimal("49"),
                annual_cost=Decimal("490"),
                api_quota=10000,
                storage_quota=50 * 1024 * 1024 * 1024,  # 50GB
                max_users=25,
                features={
                    "web_editor": True,
                    "api_access": True,
                    "custom_domain": True,
                    "audit_logs": True,
                    "sso": False,
                    "priority_support": True,
                    "webhooks": True,
                },
            ),
            SubscriptionTier.ENTERPRISE: SubscriptionConfig(
                tier=SubscriptionTier.ENTERPRISE,
                monthly_cost=Decimal("499"),
                annual_cost=Decimal("4990"),
                api_quota=100000,
                storage_quota=1024 * 1024 * 1024 * 1024,  # 1TB
                max_users=999,
                features={
                    "web_editor": True,
                    "api_access": True,
                    "custom_domain": True,
                    "audit_logs": True,
                    "sso": True,
                    "priority_support": True,
                    "webhooks": True,
                },
            ),
        }
        return configs[tier]

    def has_feature(self, feature_name: str) -> bool:
        """Check if subscription tier has a feature."""
        return self.features.get(feature_name, False)


def calculate_subscription_cost(
    tier: SubscriptionTier,
    billing_period: str = "monthly",
) -> Decimal:
    """Calculate subscription cost for given tier and billing period.

    Parameters
    ----------
    tier : SubscriptionTier
        Subscription tier.
    billing_period : str
        Billing period (monthly or annual).

    Returns
    -------
    Decimal
        Cost amount.
    """
    config = SubscriptionConfig.get_tier_config(tier)
    if billing_period == "annual":
        return config.annual_cost
    return config.monthly_cost


def check_usage_quota(
    current_usage: int,
    quota: int,
    threshold_percent: float = 0.8,
) -> dict[str, Any]:
    """Check if usage is approaching or exceeding quota.

    Parameters
    ----------
    current_usage : int
        Current usage amount.
    quota : int
        Usage quota limit.
    threshold_percent : float
        Warning threshold as percentage (0.0-1.0).

    Returns
    -------
    dict
        Quota status with keys: is_exceeded, usage_percent, warning, throttled
    """
    usage_percent = current_usage / quota if quota > 0 else 0
    is_exceeded = current_usage > quota
    warning = usage_percent >= threshold_percent

    return {
        "is_exceeded": is_exceeded,
        "usage_percent": usage_percent,
        "current_usage": current_usage,
        "quota": quota,
        "warning": warning,
        "throttled": is_exceeded,
    }


def apply_overage_charges(
    overage_amount: int,
    rate_per_unit: Decimal = Decimal("0.05"),
) -> Decimal:
    """Calculate overage charges for usage exceeding quota.

    Parameters
    ----------
    overage_amount : int
        Amount over quota (API calls, storage, etc).
    rate_per_unit : Decimal
        Cost per unit of overage.

    Returns
    -------
    Decimal
        Overage charge amount.
    """
    return Decimal(overage_amount) * rate_per_unit


# ============================================================================
# Usage Event Operations
# ============================================================================


def aggregate_usage_by_period(
    usage_events: list[dict[str, Any]],
    billing_period: str = None,
) -> dict[str, float]:
    """Aggregate usage events by metric type for a billing period.

    Parameters
    ----------
    usage_events : list
        List of usage event dictionaries.
    billing_period : str
        Filter to specific billing period (YYYY-MM).

    Returns
    -------
    dict
        Aggregated usage by metric type.
    """
    aggregated: dict[str, float] = {}

    for event in usage_events:
        if billing_period and event.get("billing_period") != billing_period:
            continue

        metric_type = event.get("metric_type", "unknown")
        amount = float(event.get("amount", 0))

        if metric_type not in aggregated:
            aggregated[metric_type] = 0
        aggregated[metric_type] += amount

    return aggregated


def get_current_billing_period() -> str:
    """Get current billing period in YYYY-MM format."""
    now = datetime.now(UTC)
    return now.strftime("%Y-%m")


def get_next_billing_period() -> str:
    """Get next billing period in YYYY-MM format."""
    now = datetime.now(UTC)
    next_month = now + timedelta(days=32)  # Account for month boundaries
    return next_month.strftime("%Y-%m")


def calculate_days_until_renewal(renewal_date: datetime) -> int:
    """Calculate days until subscription renewal.

    Parameters
    ----------
    renewal_date : datetime
        Renewal date.

    Returns
    -------
    int
        Days until renewal (negative if past).
    """
    now = datetime.now(UTC)
    renewal = renewal_date.replace(tzinfo=UTC) if renewal_date.tzinfo is None else renewal_date
    delta = renewal - now
    return delta.days


# ============================================================================
# Invoice Operations
# ============================================================================


@dataclass
class InvoiceLineItem:
    """Invoice line item."""

    description: str
    quantity: float
    unit_price: Decimal
    amount: Decimal

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": str(self.unit_price),
            "amount": str(self.amount),
        }


def generate_invoice_line_items(
    subscription_tier: SubscriptionTier,
    base_cost: Decimal,
    usage_overage: dict[str, float] | None = None,
    overage_rate: Decimal = Decimal("0.05"),
) -> tuple[list[InvoiceLineItem], Decimal]:
    """Generate invoice line items for subscription and overages.

    Parameters
    ----------
    subscription_tier : SubscriptionTier
        Subscription tier.
    base_cost : Decimal
        Base subscription cost.
    usage_overage : dict
        Usage overage by metric type.
    overage_rate : Decimal
        Rate per unit of overage.

    Returns
    -------
    tuple
        (line_items, total_amount)
    """
    line_items: list[InvoiceLineItem] = []
    total = Decimal("0")

    # Base subscription line item
    line_items.append(
        InvoiceLineItem(
            description=f"{subscription_tier.value.capitalize()} Subscription",
            quantity=1,
            unit_price=base_cost,
            amount=base_cost,
        )
    )
    total += base_cost

    # Overage charges
    if usage_overage:
        for metric_type, amount in usage_overage.items():
            overage_cost = Decimal(str(amount)) * overage_rate
            if overage_cost > 0:
                line_items.append(
                    InvoiceLineItem(
                        description=f"{metric_type.replace('_', ' ').title()} Overage",
                        quantity=amount,
                        unit_price=overage_rate,
                        amount=overage_cost,
                    )
                )
                total += overage_cost

    return line_items, total


def calculate_invoice_due_date(
    issue_date: datetime,
    days_until_due: int = 30,
) -> datetime:
    """Calculate invoice due date.

    Parameters
    ----------
    issue_date : datetime
        Invoice issue date.
    days_until_due : int
        Days until payment due.

    Returns
    -------
    datetime
        Due date.
    """
    return issue_date + timedelta(days=days_until_due)


def is_invoice_overdue(
    due_date: datetime,
    current_date: datetime | None = None,
) -> bool:
    """Check if invoice is overdue.

    Parameters
    ----------
    due_date : datetime
        Invoice due date.
    current_date : datetime
        Current date (defaults to now).

    Returns
    -------
    bool
        True if invoice is overdue.
    """
    if current_date is None:
        current_date = datetime.now(UTC)

    due = due_date.replace(tzinfo=UTC) if due_date.tzinfo is None else due_date
    current = current_date.replace(tzinfo=UTC) if current_date.tzinfo is None else current_date

    return current > due


# ============================================================================
# SLA & Support Operations
# ============================================================================


@dataclass
class SLAConfig:
    """Configuration for SLA tier."""

    tier: SLATier
    name: str
    initial_response_minutes: int
    resolution_minutes: int
    availability_percent: float
    support_hours: str
    max_concurrent_tickets: int | None

    @staticmethod
    def get_tier_config(tier: SLATier) -> SLAConfig:
        """Get configuration for SLA tier."""
        configs = {
            SLATier.COMMUNITY: SLAConfig(
                tier=SLATier.COMMUNITY,
                name="Community Support",
                initial_response_minutes=999999,  # No SLA
                resolution_minutes=999999,  # No SLA
                availability_percent=99.0,
                support_hours="best_effort",
                max_concurrent_tickets=None,
            ),
            SLATier.PROFESSIONAL: SLAConfig(
                tier=SLATier.PROFESSIONAL,
                name="Professional Support",
                initial_response_minutes=480,  # 8 hours
                resolution_minutes=10080,  # 7 days
                availability_percent=99.0,
                support_hours="business",
                max_concurrent_tickets=None,
            ),
            SLATier.ENTERPRISE: SLAConfig(
                tier=SLATier.ENTERPRISE,
                name="Enterprise Support",
                initial_response_minutes=120,  # 2 hours
                resolution_minutes=3600,  # 2.5 days
                availability_percent=99.9,
                support_hours="24/7",
                max_concurrent_tickets=None,
            ),
            SLATier.PREMIUM_ENTERPRISE: SLAConfig(
                tier=SLATier.PREMIUM_ENTERPRISE,
                name="Premium Enterprise Support",
                initial_response_minutes=30,  # 30 minutes
                resolution_minutes=1440,  # 1 day
                availability_percent=99.95,
                support_hours="24/7",
                max_concurrent_tickets=None,
            ),
        }
        return configs[tier]


def check_sla_compliance(
    created_at: datetime,
    first_response_at: datetime | None,
    resolved_at: datetime | None,
    sla_config: SLAConfig,
) -> dict[str, Any]:
    """Check if ticket is within SLA compliance.

    Parameters
    ----------
    created_at : datetime
        Ticket creation time.
    first_response_at : datetime
        First response time (None if no response yet).
    resolved_at : datetime
        Resolution time (None if unresolved).
    sla_config : SLAConfig
        SLA configuration.

    Returns
    -------
    dict
        Compliance status with keys: compliant, response_sla_met, resolution_sla_met
    """
    compliance = {
        "compliant": True,
        "response_sla_met": True,
        "resolution_sla_met": True,
        "response_minutes": None,
        "resolution_minutes": None,
    }

    # Check response SLA
    if first_response_at:
        created = created_at.replace(tzinfo=UTC) if created_at.tzinfo is None else created_at
        responded = first_response_at.replace(tzinfo=UTC) if first_response_at.tzinfo is None else first_response_at
        response_delta = responded - created
        response_minutes = response_delta.total_seconds() / 60
        compliance["response_minutes"] = response_minutes

        if response_minutes > sla_config.initial_response_minutes:
            compliance["response_sla_met"] = False
            compliance["compliant"] = False

    # Check resolution SLA
    if resolved_at:
        created = created_at.replace(tzinfo=UTC) if created_at.tzinfo is None else created_at
        resolved = resolved_at.replace(tzinfo=UTC) if resolved_at.tzinfo is None else resolved_at
        resolution_delta = resolved - created
        resolution_minutes = resolution_delta.total_seconds() / 60
        compliance["resolution_minutes"] = resolution_minutes

        if resolution_minutes > sla_config.resolution_minutes:
            compliance["resolution_sla_met"] = False
            compliance["compliant"] = False

    return compliance


# ============================================================================
# RevOps Metrics
# ============================================================================


def calculate_mrr(active_subscriptions: list[dict[str, Any]]) -> Decimal:
    """Calculate Monthly Recurring Revenue (MRR).

    Parameters
    ----------
    active_subscriptions : list
        List of active subscription dictionaries.

    Returns
    -------
    Decimal
        Total MRR.
    """
    total_mrr = Decimal("0")
    for sub in active_subscriptions:
        if sub.get("status") == "active":
            monthly_cost = Decimal(str(sub.get("monthly_cost", 0)))
            total_mrr += monthly_cost
    return total_mrr


def calculate_arr(active_subscriptions: list[dict[str, Any]]) -> Decimal:
    """Calculate Annual Recurring Revenue (ARR).

    Parameters
    ----------
    active_subscriptions : list
        List of active subscription dictionaries.

    Returns
    -------
    Decimal
        Total ARR (MRR * 12).
    """
    mrr = calculate_mrr(active_subscriptions)
    return mrr * 12


def calculate_churn_rate(
    start_count: int,
    end_count: int,
    churned_count: int,
) -> float:
    """Calculate subscription churn rate.

    Parameters
    ----------
    start_count : int
        Number of subscriptions at start of period.
    end_count : int
        Number of subscriptions at end of period.
    churned_count : int
        Number of churned subscriptions.

    Returns
    -------
    float
        Churn rate as percentage (0.0-100.0).
    """
    if start_count == 0:
        return 0.0
    return (churned_count / start_count) * 100


def calculate_ltv(
    average_monthly_revenue: Decimal,
    customer_lifespan_months: int,
) -> Decimal:
    """Calculate Customer Lifetime Value (LTV).

    Parameters
    ----------
    average_monthly_revenue : Decimal
        Average monthly revenue per customer.
    customer_lifespan_months : int
        Expected customer lifespan in months.

    Returns
    -------
    Decimal
        Customer LTV.
    """
    return average_monthly_revenue * customer_lifespan_months
