"""
specify_cli.runtime.billing - Billing Runtime Layer (Andon Pattern)
===================================================================

Database I/O and external service calls for billing operations.
Handles all side effects: database persistence, Stripe API calls, webhooks.

Implements ANDON pattern from lean manufacturing:
- Fail immediately on quality issues (no graceful degradation)
- Make errors visible and loud (raise exceptions, don't return error dicts)
- Alert operations to investigate root cause
- Enforce preconditions and state invariants

Never silently degrade. Always raise and let caller decide.

This layer coordinates between the operations layer (pure logic) and
database/external services (I/O with side effects).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from specify_cli.db.models import Invoice, InvoiceStatus, Subscription, SubscriptionTier, UsageEvent
from specify_cli.ops.billing import (
    SubscriptionConfig,
    get_current_billing_period,
    get_next_billing_period,
)
from specify_cli.runtime.billing_exceptions import (
    InvalidBillingPeriod,
    InvalidSubscriptionTier,
    InvoiceAlreadyExists,
    SubscriptionNotActive,
    SubscriptionNotFound,
    UsageTrackingFailed,
)


# ============================================================================
# Subscription Runtime Operations
# ============================================================================


def create_subscription(
    session: Session,
    user_id: int,
    tier: str = "free",
    stripe_customer_id: str | None = None,
) -> dict[str, Any]:
    """Create subscription for user in database.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.
    tier : str
        Subscription tier.
    stripe_customer_id : str
        Stripe customer ID (optional).

    Returns
    -------
    dict
        Created subscription data.

    Raises
    ------
    InvalidSubscriptionTier
        If tier is not a valid subscription tier (Andon: fail-fast).
    """
    # Validate tier (Andon: fail immediately on invalid input)
    try:
        tier_enum = SubscriptionTier(tier)
    except ValueError:
        raise InvalidSubscriptionTier(
            f"Invalid subscription tier: '{tier}'. Must be one of: free, professional, enterprise",
            error_code="INVALID_TIER",
            context={"provided_tier": tier, "valid_tiers": ["free", "professional", "enterprise"]},
        )

    config = SubscriptionConfig.get_tier_config(tier_enum)

    subscription = Subscription(
        user_id=user_id,
        tier=tier_enum,
        stripe_customer_id=stripe_customer_id,
        status="active",
        start_date=datetime.now(UTC),
        renewal_date=datetime.now(UTC) + timedelta(days=30),
        monthly_cost=config.monthly_cost,
        annual_cost=config.annual_cost,
        api_quota=config.api_quota,
        storage_quota=config.storage_quota,
        max_users=config.max_users,
    )

    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    return {
        "subscription_id": subscription.subscription_id,
        "user_id": subscription.user_id,
        "tier": subscription.tier.value,
        "status": subscription.status,
        "start_date": subscription.start_date.isoformat(),
        "renewal_date": subscription.renewal_date.isoformat(),
    }


def get_subscription(
    session: Session,
    user_id: int,
    include_cancelled: bool = False,
) -> dict[str, Any] | None:
    """Get user's subscription.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.
    include_cancelled : bool
        If True, return any subscription (active or cancelled).
        If False (default), only return active subscriptions.

    Returns
    -------
    dict or None
        Subscription data if exists.
    """
    if include_cancelled:
        # Get any subscription, active or cancelled (most recent first)
        sub = session.query(Subscription).filter(
            Subscription.user_id == user_id
        ).order_by(Subscription.start_date.desc()).first()
    else:
        # Get only active subscription
        sub = session.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
        ).first()

    if not sub:
        return None

    return {
        "subscription_id": sub.subscription_id,
        "user_id": sub.user_id,
        "tier": sub.tier.value,
        "status": sub.status,
        "start_date": sub.start_date.isoformat(),
        "renewal_date": sub.renewal_date.isoformat(),
        "api_quota": sub.api_quota,
        "storage_quota": sub.storage_quota,
        "max_users": sub.max_users,
        "stripe_customer_id": sub.stripe_customer_id,
        "stripe_subscription_id": sub.stripe_subscription_id,
        "monthly_cost": str(sub.monthly_cost),
    }


def update_subscription_tier(
    session: Session,
    user_id: int,
    new_tier: str,
) -> dict[str, Any]:
    """Upgrade or downgrade user's subscription.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.
    new_tier : str
        New subscription tier.

    Returns
    -------
    dict
        Updated subscription data.
    """
    sub = session.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
    ).first()

    if not sub:
        raise ValueError(f"No active subscription found for user {user_id}")

    # Get new tier configuration
    tier_enum = SubscriptionTier(new_tier)
    config = SubscriptionConfig.get_tier_config(tier_enum)

    # Update all tier-related fields
    sub.tier = tier_enum
    sub.monthly_cost = config.monthly_cost
    sub.annual_cost = config.annual_cost
    sub.api_quota = config.api_quota
    sub.storage_quota = config.storage_quota
    sub.max_users = config.max_users
    sub.updated_at = datetime.now(UTC)

    session.commit()
    session.refresh(sub)

    return {
        "subscription_id": sub.subscription_id,
        "user_id": sub.user_id,
        "tier": sub.tier.value,
        "api_quota": sub.api_quota,
        "storage_quota": sub.storage_quota,
        "monthly_cost": str(sub.monthly_cost),
        "updated_at": sub.updated_at.isoformat(),
    }


def cancel_subscription(
    session: Session,
    user_id: int,
) -> dict[str, Any]:
    """Cancel user's subscription.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.

    Returns
    -------
    dict
        Cancelled subscription data.
    """
    sub = session.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
    ).first()

    if not sub:
        raise ValueError(f"No active subscription found for user {user_id}")

    sub.status = "cancelled"
    sub.end_date = datetime.now(UTC)
    sub.updated_at = datetime.now(UTC)

    session.commit()
    session.refresh(sub)

    return {
        "subscription_id": sub.subscription_id,
        "status": sub.status,
        "cancelled_at": sub.end_date.isoformat(),
    }


# ============================================================================
# Usage Event Runtime Operations
# ============================================================================


def track_usage_event(
    session: Session,
    user_id: int,
    metric_type: str,
    amount: float,
) -> dict[str, Any]:
    """Record usage event for metered billing.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.
    metric_type : str
        Type of usage (api_calls, storage, etc).
    amount : float
        Amount consumed.

    Returns
    -------
    dict
        Recorded usage event.

    Raises
    ------
    SubscriptionNotFound
        If user has no active subscription (Andon: fail-fast).
    """
    # Get user's subscription (Andon: fail if not active)
    sub = session.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
    ).first()

    if not sub:
        raise SubscriptionNotActive(
            f"Cannot track usage: user {user_id} has no active subscription",
            error_code="NO_ACTIVE_SUBSCRIPTION",
            context={"user_id": user_id},
        )

    billing_period = get_current_billing_period()

    try:
        event = UsageEvent(
            subscription_id=sub.id,
            user_id=user_id,
            metric_type=metric_type,
            amount=amount,
            billing_period=billing_period,
        )

        session.add(event)
        session.commit()
        session.refresh(event)
    except Exception as e:
        session.rollback()
        raise UsageTrackingFailed(
            f"Failed to track usage for user {user_id}: {str(e)}",
            error_code="USAGE_TRACKING_ERROR",
            context={"user_id": user_id, "metric_type": metric_type, "amount": amount},
        ) from e

    return {
        "event_id": event.event_id,
        "user_id": user_id,
        "metric_type": metric_type,
        "amount": amount,
        "billing_period": billing_period,
        "timestamp": event.timestamp.isoformat(),
    }


def get_usage_for_period(
    session: Session,
    user_id: int,
    billing_period: str | None = None,
) -> dict[str, float]:
    """Get aggregated usage for user in billing period.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.
    billing_period : str
        Billing period (YYYY-MM). Defaults to current.

    Returns
    -------
    dict
        Aggregated usage by metric type.
    """
    if not billing_period:
        billing_period = get_current_billing_period()

    events = session.query(UsageEvent).filter(
        UsageEvent.user_id == user_id,
        UsageEvent.billing_period == billing_period,
    ).all()

    aggregated: dict[str, float] = {}
    for event in events:
        if event.metric_type not in aggregated:
            aggregated[event.metric_type] = 0
        aggregated[event.metric_type] += event.amount

    return aggregated


def get_usage_quota_status(
    session: Session,
    user_id: int,
) -> dict[str, Any]:
    """Get current usage against quota for user.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.

    Returns
    -------
    dict
        Usage quota status.
    """
    # Get subscription
    sub = session.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
    ).first()

    if not sub:
        return {"error": "No active subscription"}

    # Get current usage
    usage = get_usage_for_period(session, user_id)
    api_calls_used = usage.get("api_calls", 0)

    return {
        "tier": sub.tier.value,
        "api_quota": sub.api_quota,
        "api_calls_used": int(api_calls_used),
        "remaining": max(0, sub.api_quota - int(api_calls_used)),
        "percentage_used": (api_calls_used / sub.api_quota * 100) if sub.api_quota > 0 else 0,
        "warning": (api_calls_used / sub.api_quota) >= 0.8 if sub.api_quota > 0 else False,
        "exceeded": api_calls_used > sub.api_quota,
    }


# ============================================================================
# Invoice Runtime Operations
# ============================================================================


def generate_invoice(
    session: Session,
    user_id: int,
    billing_period: str | None = None,
) -> dict[str, Any]:
    """Generate invoice for subscription at period end.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.
    billing_period : str
        Billing period to invoice. Defaults to current month.

    Returns
    -------
    dict
        Generated invoice data.

    Raises
    ------
    InvalidBillingPeriod
        If billing period format is invalid (Andon: strict validation).
    SubscriptionNotActive
        If user has no active subscription (Andon: enforce preconditions).
    InvoiceAlreadyExists
        If invoice already exists for period (Andon: prevent duplicates).
    """
    if not billing_period:
        billing_period = get_current_billing_period()

    # Validate billing period format (Andon: fail immediately on invalid format)
    try:
        parts = billing_period.split("-")
        if len(parts) != 2:
            raise InvalidBillingPeriod(
                f"Invalid billing period format: '{billing_period}'. Expected YYYY-MM",
                error_code="INVALID_PERIOD_FORMAT",
                context={"provided": billing_period},
            )
        year_str, month_str = parts
        year = int(year_str)  # Validate it's numeric
        month = int(month_str)  # Validate it's numeric

        # Validate month range
        if month < 1 or month > 12:
            raise InvalidBillingPeriod(
                f"Invalid billing period: month must be 1-12, got {month}",
                error_code="INVALID_MONTH",
                context={"provided": billing_period, "month": month},
            )
    except ValueError as e:
        if isinstance(e, InvalidBillingPeriod):
            raise
        raise InvalidBillingPeriod(
            f"Invalid billing period format: '{billing_period}'. Expected YYYY-MM",
            error_code="INVALID_PERIOD_FORMAT",
            context={"provided": billing_period},
        ) from e

    # Get subscription (Andon: fail if not active)
    sub = session.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
    ).first()

    if not sub:
        raise SubscriptionNotActive(
            f"Cannot generate invoice: user {user_id} has no active subscription",
            error_code="NO_ACTIVE_SUBSCRIPTION",
            context={"user_id": user_id, "billing_period": billing_period},
        )

    # Check if invoice already exists (Andon: prevent duplicates)
    existing = session.query(Invoice).filter(
        Invoice.subscription_id == sub.id,
        Invoice.billing_period_start.like(f"{billing_period}%"),
    ).first()

    if existing:
        raise InvoiceAlreadyExists(
            f"Invoice already exists for user {user_id} in period {billing_period}",
            error_code="DUPLICATE_INVOICE",
            context={"user_id": user_id, "billing_period": billing_period, "invoice_id": existing.invoice_id},
        )

    # Parse billing period
    year, month = billing_period.split("-")
    start_date = datetime(int(year), int(month), 1, tzinfo=UTC)

    # Calculate end date (last day of month)
    if month == "12":
        end_date = datetime(int(year) + 1, 1, 1, tzinfo=UTC) - timedelta(seconds=1)
    else:
        end_date = datetime(int(year), int(month) + 1, 1, tzinfo=UTC) - timedelta(seconds=1)

    # Get usage for period
    usage = get_usage_for_period(session, user_id, billing_period)

    # Calculate amount
    amount = sub.monthly_cost
    line_items = [
        {
            "description": f"{sub.tier.value.capitalize()} Subscription",
            "quantity": 1,
            "unit_price": str(sub.monthly_cost),
            "amount": str(sub.monthly_cost),
        }
    ]

    # Add overage charges (API calls over quota at $0.05/call)
    api_calls_used = int(usage.get("api_calls", 0))
    if api_calls_used > sub.api_quota:
        overage = api_calls_used - sub.api_quota
        overage_cost = Decimal(str(overage)) * Decimal("0.05")
        amount += overage_cost
        line_items.append(
            {
                "description": f"API Calls Overage ({overage} calls)",
                "quantity": overage,
                "unit_price": "0.05",
                "amount": str(overage_cost),
            }
        )

    # Create invoice
    due_date = start_date + timedelta(days=30)
    invoice = Invoice(
        subscription_id=sub.id,
        user_id=user_id,
        amount=amount,
        status=InvoiceStatus.DRAFT,
        billing_period_start=start_date,
        billing_period_end=end_date,
        due_date=due_date,
        line_items=line_items,
    )

    session.add(invoice)
    session.commit()
    session.refresh(invoice)

    return {
        "invoice_id": invoice.invoice_id,
        "subscription_id": sub.subscription_id,
        "amount": str(invoice.amount),
        "status": invoice.status.value,
        "issue_date": invoice.issue_date.isoformat(),
        "due_date": invoice.due_date.isoformat(),
        "line_items": line_items,
    }


def get_invoices(
    session: Session,
    user_id: int,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Get user's invoices.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    user_id : int
        User ID.
    limit : int
        Maximum invoices to return.

    Returns
    -------
    list
        List of invoice records.
    """
    invoices = session.query(Invoice).filter(
        Invoice.user_id == user_id,
    ).order_by(Invoice.issue_date.desc()).limit(limit).all()

    result = []
    for inv in invoices:
        result.append(
            {
                "invoice_id": inv.invoice_id,
                "amount": str(inv.amount),
                "status": inv.status.value,
                "issue_date": inv.issue_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "paid_date": inv.paid_date.isoformat() if inv.paid_date else None,
                "line_items": inv.line_items,
            }
        )

    return result


def mark_invoice_paid(
    session: Session,
    invoice_id: str,
    stripe_invoice_id: str | None = None,
) -> dict[str, Any]:
    """Mark invoice as paid (typically from Stripe webhook).

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    invoice_id : str
        Invoice UUID.
    stripe_invoice_id : str
        Stripe invoice ID (for webhook tracking).

    Returns
    -------
    dict
        Updated invoice data.
    """
    invoice = session.query(Invoice).filter(
        Invoice.invoice_id == invoice_id,
    ).first()

    if not invoice:
        raise ValueError(f"Invoice not found: {invoice_id}")

    invoice.status = InvoiceStatus.PAID
    invoice.paid_date = datetime.now(UTC)
    if stripe_invoice_id:
        invoice.stripe_invoice_id = stripe_invoice_id
    invoice.updated_at = datetime.now(UTC)

    session.commit()
    session.refresh(invoice)

    return {
        "invoice_id": invoice.invoice_id,
        "status": invoice.status.value,
        "paid_date": invoice.paid_date.isoformat(),
    }


# ============================================================================
# Reporting & Analytics
# ============================================================================


def get_mrr(session: Session) -> Decimal:
    """Get total Monthly Recurring Revenue.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.

    Returns
    -------
    Decimal
        Total MRR.
    """
    result = session.query(func.sum(Subscription.monthly_cost)).filter(
        Subscription.status == "active",
    ).scalar()

    return result or Decimal("0")


def get_active_subscription_count(session: Session) -> int:
    """Get count of active subscriptions.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.

    Returns
    -------
    int
        Number of active subscriptions.
    """
    return session.query(Subscription).filter(
        Subscription.status == "active",
    ).count()


def get_revenue_by_tier(session: Session) -> dict[str, Any]:
    """Get MRR breakdown by subscription tier.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.

    Returns
    -------
    dict
        Revenue by tier.
    """
    results = session.query(
        Subscription.tier,
        func.count(Subscription.id),
        func.sum(Subscription.monthly_cost),
    ).filter(
        Subscription.status == "active",
    ).group_by(Subscription.tier).all()

    revenue_by_tier = {}
    total_mrr = Decimal("0")

    for tier, count, revenue in results:
        tier_name = tier.value if hasattr(tier, "value") else str(tier)
        revenue_amount = revenue or Decimal("0")
        revenue_by_tier[tier_name] = {
            "count": count,
            "mrr": str(revenue_amount),
        }
        total_mrr += revenue_amount

    revenue_by_tier["total"] = str(total_mrr)
    return revenue_by_tier
