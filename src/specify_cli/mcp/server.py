"""
specify_cli.mcp.server - RevOps MCP Server

Exposes Revenue Operations infrastructure as MCP tools and resources.
Enables Claude and other MCP clients to manage subscriptions, track usage,
generate invoices, and analyze revenue metrics.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from specify_cli.db.models import Base, Subscription, UsageEvent, Invoice
from specify_cli.ops.billing import (
    SubscriptionConfig,
    calculate_mrr,
    calculate_arr,
    check_usage_quota,
)
from specify_cli.runtime.billing import (
    create_subscription as runtime_create_subscription,
    get_subscription as runtime_get_subscription,
    update_subscription_tier as runtime_update_subscription_tier,
    cancel_subscription as runtime_cancel_subscription,
    track_usage_event as runtime_track_usage_event,
    get_usage_for_period as runtime_get_usage_for_period,
    get_usage_quota_status as runtime_get_usage_quota_status,
    generate_invoice as runtime_generate_invoice,
    get_invoices as runtime_get_invoices,
    mark_invoice_paid as runtime_mark_invoice_paid,
    get_mrr as runtime_get_mrr,
    get_revenue_by_tier as runtime_get_revenue_by_tier,
)
from specify_cli.runtime.billing_poka_yoke import (
    validate_and_suggest_tier,
    parse_billing_period,
    validate_user_id,
    validate_amount,
    adapt_subscription_error,
)
from specify_cli.security.subscription_enforcement import (
    TierFeatures,
    SubscriptionEnforcer,
)

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None


def create_revops_server(database_url: str = "sqlite:///:memory:") -> FastMCP:
    """
    Create and configure the RevOps MCP server.

    Parameters
    ----------
    database_url : str
        Database connection URL. Defaults to in-memory SQLite.

    Returns
    -------
    FastMCP
        Configured MCP server with RevOps tools.

    Raises
    ------
    ImportError
        If fastmcp is not installed.
    """
    if FastMCP is None:
        raise ImportError("fastmcp must be installed. Install with: pip install fastmcp")

    # Initialize server
    mcp = FastMCP(
        "RevOps Server",
        description="Revenue Operations infrastructure for ggen-spec-kit",
    )

    # Create database engine and session factory
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    # ========================================================================
    # Subscription Management Tools
    # ========================================================================

    @mcp.tool
    def create_subscription(
        user_id: int,
        tier: str = "free",
        stripe_customer_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new subscription for a user.

        Parameters
        ----------
        user_id : int
            Unique user identifier
        tier : str
            Subscription tier (free, professional, enterprise)
        stripe_customer_id : str, optional
            Stripe customer ID for payment integration

        Returns
        -------
        dict
            Created subscription details or error dict with recovery hints
        """
        session = SessionLocal()
        try:
            # Poka Yoke Level 1: Input validation
            validated_user_id = validate_user_id(user_id)
            validated_tier, suggestion = validate_and_suggest_tier(tier)

            # If tier was suggested, include warning in response but use validated tier
            result = runtime_create_subscription(
                session, validated_user_id, validated_tier, stripe_customer_id
            )

            if suggestion and suggestion != tier:
                result["warning"] = f"Tier '{tier}' was corrected to '{suggestion}'"
                result["correction_applied"] = True

            return result
        except ValueError as e:
            # Poka Yoke Level 2: Input validation errors
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_INPUT",
                "recovery": ["Ensure user_id is a positive integer", "Ensure tier is: free, professional, or enterprise"],
            }
        except Exception as e:
            # Poka Yoke Level 2: Error adaptation for domain exceptions
            return adapt_subscription_error(e, {"user_id": user_id, "tier": tier})
        finally:
            session.close()

    @mcp.tool
    def get_subscription(user_id: int) -> dict[str, Any] | None:
        """
        Retrieve active subscription for a user.

        Parameters
        ----------
        user_id : int
            Unique user identifier

        Returns
        -------
        dict or None
            Subscription details if exists, None otherwise
        """
        session = SessionLocal()
        try:
            return runtime_get_subscription(session, user_id)
        finally:
            session.close()

    @mcp.tool
    def upgrade_subscription(user_id: int, new_tier: str) -> dict[str, Any]:
        """
        Upgrade or downgrade a subscription to a different tier.

        Parameters
        ----------
        user_id : int
            Unique user identifier
        new_tier : str
            Target subscription tier (free, professional, enterprise)

        Returns
        -------
        dict
            Updated subscription details or error dict with recovery hints
        """
        session = SessionLocal()
        try:
            # Poka Yoke Level 1: Input validation
            validated_user_id = validate_user_id(user_id)
            validated_tier, suggestion = validate_and_suggest_tier(new_tier)

            # If tier was suggested, include warning in response but use validated tier
            result = runtime_update_subscription_tier(session, validated_user_id, validated_tier)

            if suggestion and suggestion != new_tier:
                result["warning"] = f"Tier '{new_tier}' was corrected to '{suggestion}'"
                result["correction_applied"] = True

            return result
        except ValueError as e:
            # Poka Yoke Level 2: Input validation errors
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_INPUT",
                "recovery": ["Ensure user_id is a positive integer", "Ensure new_tier is: free, professional, or enterprise"],
            }
        except Exception as e:
            # Poka Yoke Level 2: Error adaptation for domain exceptions
            return adapt_subscription_error(e, {"user_id": user_id, "new_tier": new_tier})
        finally:
            session.close()

    @mcp.tool
    def cancel_subscription(user_id: int) -> dict[str, Any]:
        """
        Cancel an active subscription.

        Parameters
        ----------
        user_id : int
            Unique user identifier

        Returns
        -------
        dict
            Cancellation confirmation with end date
        """
        session = SessionLocal()
        try:
            return runtime_cancel_subscription(session, user_id)
        finally:
            session.close()

    # ========================================================================
    # Usage Tracking and Quota Management
    # ========================================================================

    @mcp.tool
    def track_usage(
        user_id: int,
        metric_type: str,
        amount: float,
    ) -> dict[str, Any]:
        """
        Track usage event for metered billing.

        Parameters
        ----------
        user_id : int
            Unique user identifier
        metric_type : str
            Type of usage (api_calls, storage, webhooks)
        amount : float
            Amount consumed in this billing period

        Returns
        -------
        dict
            Event confirmation with timestamp or error dict with recovery hints
        """
        session = SessionLocal()
        try:
            # Poka Yoke Level 1: Input validation
            validated_user_id = validate_user_id(user_id)
            validated_amount = validate_amount(amount)

            return runtime_track_usage_event(
                session, validated_user_id, metric_type, validated_amount
            )
        except ValueError as e:
            # Poka Yoke Level 2: Input validation errors
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_INPUT",
                "recovery": ["Ensure user_id is a positive integer", "Ensure amount is numeric (positive, zero, or negative for credits)"],
            }
        except Exception as e:
            # Poka Yoke Level 2: Error adaptation for domain exceptions
            return adapt_subscription_error(e, {"user_id": user_id, "metric_type": metric_type, "amount": amount})
        finally:
            session.close()

    @mcp.tool
    def get_usage_status(user_id: int) -> dict[str, Any]:
        """
        Get current usage status against quota for a user.

        Parameters
        ----------
        user_id : int
            Unique user identifier

        Returns
        -------
        dict
            Usage status with tier, quota, usage, remaining, percentage, warnings
        """
        session = SessionLocal()
        try:
            return runtime_get_usage_quota_status(session, user_id)
        finally:
            session.close()

    @mcp.tool
    def get_usage_history(
        user_id: int,
        billing_period: str | None = None,
    ) -> dict[str, float]:
        """
        Get aggregated usage for a billing period.

        Parameters
        ----------
        user_id : int
            Unique user identifier
        billing_period : str, optional
            Billing period (YYYY-MM). Defaults to current month.

        Returns
        -------
        dict
            Aggregated usage by metric type
        """
        session = SessionLocal()
        try:
            return runtime_get_usage_for_period(session, user_id, billing_period)
        finally:
            session.close()

    # ========================================================================
    # Invoicing and Payments
    # ========================================================================

    @mcp.tool
    def generate_invoice(
        user_id: int,
        billing_period: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate invoice for a user in a billing period.

        Parameters
        ----------
        user_id : int
            Unique user identifier
        billing_period : str, optional
            Billing period (YYYY-MM, Jan 2026, January 2026, etc). Defaults to current month.

        Returns
        -------
        dict
            Invoice details with amount, status, line items, due date or error dict with recovery hints
        """
        session = SessionLocal()
        try:
            # Poka Yoke Level 1: Input validation
            validated_user_id = validate_user_id(user_id)

            # Parse billing period if provided (Poka Yoke: accepts multiple formats)
            if billing_period:
                parsed_period = parse_billing_period(billing_period)
            else:
                parsed_period = None

            return runtime_generate_invoice(session, validated_user_id, parsed_period)
        except ValueError as e:
            # Poka Yoke Level 2: Input validation errors
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_INPUT",
                "recovery": ["Ensure user_id is a positive integer"],
            }
        except Exception as e:
            # Poka Yoke Level 2: Error adaptation for domain exceptions
            return adapt_subscription_error(e, {"user_id": user_id, "billing_period": billing_period})
        finally:
            session.close()

    @mcp.tool
    def get_invoices(user_id: int, limit: int = 12) -> list[dict[str, Any]]:
        """
        Get invoice history for a user.

        Parameters
        ----------
        user_id : int
            Unique user identifier
        limit : int
            Maximum number of invoices to return (default 12)

        Returns
        -------
        list
            List of invoice records, most recent first
        """
        session = SessionLocal()
        try:
            return runtime_get_invoices(session, user_id, limit)
        finally:
            session.close()

    @mcp.tool
    def mark_payment_received(
        invoice_id: str,
        stripe_invoice_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Mark invoice as paid (typically from Stripe webhook).

        Parameters
        ----------
        invoice_id : str
            Invoice UUID
        stripe_invoice_id : str, optional
            Stripe invoice ID for cross-reference

        Returns
        -------
        dict
            Updated invoice with paid_date and status
        """
        session = SessionLocal()
        try:
            return runtime_mark_invoice_paid(session, invoice_id, stripe_invoice_id)
        finally:
            session.close()

    # ========================================================================
    # Revenue Metrics and Analytics
    # ========================================================================

    @mcp.tool
    def get_monthly_recurring_revenue() -> str:
        """
        Get total Monthly Recurring Revenue (MRR).

        Returns
        -------
        str
            MRR as decimal string (currency)
        """
        session = SessionLocal()
        try:
            mrr = runtime_get_mrr(session)
            return str(mrr)
        finally:
            session.close()

    @mcp.tool
    def get_annual_recurring_revenue() -> str:
        """
        Get total Annual Recurring Revenue (ARR).

        Returns
        -------
        str
            ARR as decimal string (MRR × 12)
        """
        session = SessionLocal()
        try:
            mrr = runtime_get_mrr(session)
            from specify_cli.ops.billing import calculate_arr as ops_calculate_arr

            subscriptions = (
                session.query(Subscription)
                .filter(Subscription.status == "active")
                .all()
            )
            subs_data = [
                {"monthly_cost": float(sub.monthly_cost)} for sub in subscriptions
            ]
            arr = ops_calculate_arr(subs_data)
            return str(arr)
        finally:
            session.close()

    @mcp.tool
    def get_revenue_breakdown() -> dict[str, Any]:
        """
        Get revenue metrics broken down by subscription tier.

        Returns
        -------
        dict
            Revenue data by tier with count and MRR
        """
        session = SessionLocal()
        try:
            return runtime_get_revenue_by_tier(session)
        finally:
            session.close()

    # ========================================================================
    # Feature Access Control
    # ========================================================================

    @mcp.tool
    def check_feature_access(user_tier: str, feature: str) -> dict[str, Any]:
        """
        Check if a subscription tier has access to a feature.

        Parameters
        ----------
        user_tier : str
            Subscription tier (free, professional, enterprise)
        feature : str
            Feature to check access for

        Returns
        -------
        dict
            Access check result with allowed, required_tier, reason
        """
        enforcer = SubscriptionEnforcer()
        return enforcer.check_feature_access(user_tier, feature)

    @mcp.tool
    def get_tier_features(tier: str) -> list[str]:
        """
        Get all features available in a subscription tier.

        Parameters
        ----------
        tier : str
            Subscription tier (free, professional, enterprise)

        Returns
        -------
        list
            List of available features
        """
        return TierFeatures.get_features_for_tier(tier)

    @mcp.tool
    def get_tier_limits(tier: str) -> dict[str, int]:
        """
        Get rate limits and quotas for a subscription tier.

        Parameters
        ----------
        tier : str
            Subscription tier (free, professional, enterprise)

        Returns
        -------
        dict
            Tier limits with API calls, storage, team members, RPS
        """
        enforcer = SubscriptionEnforcer()
        return enforcer.get_tier_limits(tier)

    # ========================================================================
    # Subscription Configuration
    # ========================================================================

    @mcp.tool
    def get_subscription_tiers() -> dict[str, Any]:
        """
        Get configuration for all subscription tiers.

        Returns
        -------
        dict
            Tier configurations including pricing, quotas, and features
        """
        tiers_config = {}

        for tier_name in ["free", "professional", "enterprise"]:
            from specify_cli.db.models import SubscriptionTier

            tier_enum = SubscriptionTier(tier_name)
            config = SubscriptionConfig.get_tier_config(tier_enum)

            tiers_config[tier_name] = {
                "monthly_cost": str(config.monthly_cost),
                "annual_cost": str(config.annual_cost),
                "api_quota": config.api_quota,
                "storage_quota": config.storage_quota,
                "max_users": config.max_users,
                "features": TierFeatures.get_features_for_tier(tier_name),
            }

        return tiers_config

    # ========================================================================
    # System Information
    # ========================================================================

    @mcp.tool
    def get_revops_status() -> dict[str, Any]:
        """
        Get current RevOps system status.

        Returns
        -------
        dict
            System status with version, subscriptions, users, MRR
        """
        session = SessionLocal()
        try:
            from sqlalchemy import func

            active_count = (
                session.query(func.count(Subscription.id))
                .filter(Subscription.status == "active")
                .scalar()
            )
            user_count = (
                session.query(func.count(Subscription.user_id.distinct())).scalar()
            )
            mrr = runtime_get_mrr(session)

            return {
                "version": "1.0.0",
                "status": "healthy",
                "active_subscriptions": active_count or 0,
                "total_users": user_count or 0,
                "mrr": str(mrr),
                "timestamp": datetime.now().isoformat(),
            }
        finally:
            session.close()

    return mcp


if __name__ == "__main__":
    # Run standalone MCP server
    import asyncio

    async def main():
        server = create_revops_server("sqlite:///./revops.db")
        print("RevOps MCP Server started")

    asyncio.run(main())
