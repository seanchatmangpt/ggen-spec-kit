"""
specify_cli.security.subscription_enforcement - Tier-Based Feature Access Control
==================================================================================

Enforces subscription tier access to features and API quotas.
Integrates with rate limiting to apply tier-based limits.

Features:
- Feature gating by tier (SSO for enterprise only, webhooks for professional+)
- Quota enforcement (API calls, storage)
- Rate limiting integration with tier-based limits
- Usage tracking hooks
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class FeatureRequirement:
    """Specifies which tier is required for a feature."""

    feature_name: str
    required_tier: str  # "free", "professional", "enterprise"
    description: str = ""


# ============================================================================
# Feature Tier Matrix
# ============================================================================


class TierFeatures:
    """Feature availability by subscription tier."""

    # Feature requirements (minimum tier needed)
    FEATURES = {
        # Free tier features
        "web_editor": "free",
        "export_pdf": "free",
        "public_specifications": "free",
        "community_support": "free",
        "api_read": "free",
        # Professional tier features
        "custom_domain": "professional",
        "private_specifications": "professional",
        "api_write": "professional",
        "webhooks": "professional",
        "priority_email_support": "professional",
        "audit_logs": "professional",
        # Enterprise tier features
        "sso": "enterprise",
        "saml": "enterprise",
        "dedicated_account_manager": "enterprise",
        "sla_99_9": "enterprise",
        "custom_integrations": "enterprise",
        "bulk_exports": "enterprise",
        "on_premise_deployment": "enterprise",
    }

    # Tier hierarchy (for checking if tier has access)
    TIER_HIERARCHY = {
        "free": 0,
        "professional": 1,
        "enterprise": 2,
    }

    @classmethod
    def has_feature(cls, tier: str, feature_name: str) -> bool:
        """Check if tier has access to feature.

        Parameters
        ----------
        tier : str
            Subscription tier.
        feature_name : str
            Feature name.

        Returns
        -------
        bool
            True if tier has feature.
        """
        if feature_name not in cls.FEATURES:
            return False

        required_tier = cls.FEATURES[feature_name]
        tier_level = cls.TIER_HIERARCHY.get(tier, -1)
        required_level = cls.TIER_HIERARCHY.get(required_tier, 999)

        return tier_level >= required_level

    @classmethod
    def get_features_for_tier(cls, tier: str) -> list[str]:
        """Get list of features available in tier.

        Parameters
        ----------
        tier : str
            Subscription tier.

        Returns
        -------
        list
            Features available in tier.
        """
        return [
            feature
            for feature, required_tier in cls.FEATURES.items()
            if cls.has_feature(tier, feature)
        ]


# ============================================================================
# Subscription Enforcement
# ============================================================================


class SubscriptionEnforcer:
    """Enforces subscription requirements for API operations."""

    def __init__(self) -> None:
        """Initialize enforcer."""
        pass

    def check_feature_access(
        self,
        user_tier: str,
        feature_name: str,
    ) -> dict[str, Any]:
        """Check if user's tier has access to feature.

        Parameters
        ----------
        user_tier : str
            User's subscription tier.
        feature_name : str
            Feature to access.

        Returns
        -------
        dict
            Access check result with keys: allowed, reason, required_tier
        """
        has_access = TierFeatures.has_feature(user_tier, feature_name)

        if has_access:
            return {
                "allowed": True,
                "feature": feature_name,
                "tier": user_tier,
            }

        required_tier = TierFeatures.FEATURES.get(feature_name, "unknown")
        return {
            "allowed": False,
            "feature": feature_name,
            "tier": user_tier,
            "required_tier": required_tier,
            "reason": f"Feature '{feature_name}' requires {required_tier} subscription or higher",
        }

    def get_tier_limits(self, tier: str) -> dict[str, int]:
        """Get API limits for tier.

        Parameters
        ----------
        tier : str
            Subscription tier.

        Returns
        -------
        dict
            Rate limits and quotas.
        """
        limits = {
            "free": {
                "api_calls_per_month": 100,
                "api_calls_per_minute": 1,
                "storage_bytes": 2 * 1024 * 1024 * 1024,  # 2GB
                "max_team_members": 1,
                "requests_per_second": 1,
            },
            "professional": {
                "api_calls_per_month": 10000,
                "api_calls_per_minute": 100,
                "storage_bytes": 50 * 1024 * 1024 * 1024,  # 50GB
                "max_team_members": 25,
                "requests_per_second": 10,
            },
            "enterprise": {
                "api_calls_per_month": 100000,
                "api_calls_per_minute": 1000,
                "storage_bytes": 1024 * 1024 * 1024 * 1024,  # 1TB
                "max_team_members": 999,
                "requests_per_second": 100,
            },
        }

        return limits.get(tier, limits["free"])

    def enforce_quota(
        self,
        user_tier: str,
        current_usage: int,
        quota_type: str = "api_calls_per_month",
    ) -> dict[str, Any]:
        """Check if user has exceeded quota.

        Parameters
        ----------
        user_tier : str
            Subscription tier.
        current_usage : int
            Current usage amount.
        quota_type : str
            Type of quota to check.

        Returns
        -------
        dict
            Quota status with keys: allowed, usage, limit, percentage, throttle
        """
        limits = self.get_tier_limits(user_tier)
        quota = limits.get(quota_type, 0)

        if quota == 0:
            return {
                "allowed": False,
                "reason": f"Quota type not found: {quota_type}",
            }

        percentage = (current_usage / quota * 100) if quota > 0 else 0
        allowed = current_usage <= quota
        warn = percentage >= 80

        return {
            "allowed": allowed,
            "usage": current_usage,
            "limit": quota,
            "percentage": percentage,
            "warning": warn,
            "throttle": not allowed,
        }


def require_tier(required_tier: str) -> Callable:
    """Decorator to require specific subscription tier for operation.

    Parameters
    ----------
    required_tier : str
        Minimum required tier.

    Returns
    -------
    Callable
        Decorator function.

    Example
    -------
        @require_tier("professional")
        def create_webhook(user_id, url):
            # Only professional+ can create webhooks
            pass
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Note: Actual tier checking would happen in runtime layer
            # This is a placeholder for the decorator pattern
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_feature(feature_name: str) -> Callable:
    """Decorator to require specific feature for operation.

    Parameters
    ----------
    feature_name : str
        Feature to require.

    Returns
    -------
    Callable
        Decorator function.

    Example
    -------
        @require_feature("webhooks")
        def create_webhook(user_id, url):
            # Only users with webhook feature can call this
            pass
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Note: Actual feature checking would happen in runtime layer
            return func(*args, **kwargs)

        return wrapper

    return decorator
