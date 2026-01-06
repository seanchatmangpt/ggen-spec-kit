"""
Poka Yoke (Mistake-Proofing) for Billing Operations
===================================================

Implements mistake-proofing mechanisms to prevent MCP agent confusion:
1. Input validation before runtime calls (prevent at source)
2. Exception adaptation to clear error messages (make errors obvious)
3. Pre-condition checks (fail fast, clean)
4. Recovery hints for user guidance (make it easy to fix)

Poka Yoke Principle: Make it impossible, obvious, and easy to do the right thing.
"""

from __future__ import annotations

import re
from datetime import datetime
from difflib import get_close_matches
from typing import Any

from specify_cli.ops.billing import SubscriptionTier
from specify_cli.runtime.billing_exceptions import (
    InvalidBillingPeriod,
    InvalidSubscriptionTier,
)


# ============================================================================
# Tier Validation & Suggestion
# ============================================================================


def validate_and_suggest_tier(tier_input: str) -> tuple[str, str | None]:
    """Validate tier, suggest correction if invalid.

    Parameters
    ----------
    tier_input : str
        User-provided tier string.

    Returns
    -------
    tuple[str, str | None]
        (validated_tier, suggestion) where suggestion is None if valid,
        or the suggested tier if user meant something else.

    Raises
    ------
    InvalidSubscriptionTier
        If tier is completely unrecognizable (Andon pattern).
    """
    valid_tiers = {"free", "professional", "enterprise"}
    tier_lower = tier_input.lower().strip()

    # Exact match (case-insensitive)
    if tier_lower in valid_tiers:
        return tier_lower, None

    # Common user mistakes
    common_mistakes = {
        "standard": "professional",
        "pro": "professional",
        "basic": "free",
        "premium": "enterprise",
        "gold": "enterprise",
        "silver": "professional",
        "starter": "free",
        "paid": "professional",
        "business": "enterprise",
        "enterprise tier": "enterprise",
        "pro tier": "professional",
    }

    if tier_lower in common_mistakes:
        suggested = common_mistakes[tier_lower]
        return suggested, suggested

    # Fuzzy match (edit distance)
    close_matches = get_close_matches(tier_lower, valid_tiers, n=1, cutoff=0.6)
    if close_matches:
        suggested = close_matches[0]
        return suggested, suggested

    # No match found - raise with context (Andon)
    raise InvalidSubscriptionTier(
        f"Cannot recognize subscription tier: '{tier_input}'",
        error_code="UNRECOGNIZED_TIER",
        context={
            "provided": tier_input,
            "valid_options": list(valid_tiers),
            "common_mistakes": {
                "standard": "use 'professional' instead",
                "pro": "use 'professional' instead",
                "basic": "use 'free' instead",
                "premium": "use 'enterprise' instead",
            },
        },
    )


# ============================================================================
# Billing Period Parsing & Validation
# ============================================================================


def parse_billing_period(user_input: str) -> str:
    """Parse user input into YYYY-MM format.

    Accepts multiple formats:
    - "2026-01" (YYYY-MM) - direct
    - "01-2026" (MM-YYYY) - reversed
    - "2026/01" (YYYY/MM) - slash
    - "Jan 2026" (Mon YYYY) - month abbreviation
    - "January 2026" (Month YYYY) - full month name

    Parameters
    ----------
    user_input : str
        User-provided billing period string.

    Returns
    -------
    str
        Normalized period in YYYY-MM format.

    Raises
    ------
    InvalidBillingPeriod
        If format cannot be parsed or month invalid (Andon pattern).
    """
    user_input = user_input.strip()

    # Try numeric formats with regex
    numeric_formats = [
        (r"^(\d{4})-(\d{1,2})$", lambda m: (m.group(1), m.group(2))),  # 2026-01
        (r"^(\d{1,2})-(\d{4})$", lambda m: (m.group(2), m.group(1))),  # 01-2026
        (r"^(\d{4})/(\d{1,2})$", lambda m: (m.group(1), m.group(2))),  # 2026/01
        (r"^(\d{1,2})/(\d{4})$", lambda m: (m.group(2), m.group(1))),  # 01/2026
    ]

    for pattern, extractor in numeric_formats:
        if match := re.match(pattern, user_input):
            try:
                year, month = extractor(match)
                month_int = int(month)

                if 1 <= month_int <= 12:
                    return f"{year}-{month_int:02d}"
                else:
                    raise InvalidBillingPeriod(
                        f"Invalid month {month_int} in period: '{user_input}'",
                        error_code="INVALID_MONTH",
                        context={
                            "provided": user_input,
                            "month": month_int,
                            "valid_range": "1-12",
                        },
                    )
            except (ValueError, AttributeError):
                pass

    # Try month name parsing (full name)
    try:
        parsed = datetime.strptime(user_input, "%B %Y")  # "January 2026"
        return parsed.strftime("%Y-%m")
    except ValueError:
        pass

    # Try month abbreviation
    try:
        parsed = datetime.strptime(user_input, "%b %Y")  # "Jan 2026"
        return parsed.strftime("%Y-%m")
    except ValueError:
        pass

    # Try reversed month name
    try:
        parsed = datetime.strptime(user_input, "%Y %B")  # "2026 January"
        return parsed.strftime("%Y-%m")
    except ValueError:
        pass

    # All formats failed - clear error with examples
    raise InvalidBillingPeriod(
        f"Cannot parse billing period: '{user_input}'",
        error_code="INVALID_PERIOD_FORMAT",
        context={
            "provided": user_input,
            "accepted_formats": [
                "2026-01 (YYYY-MM format)",
                "01-2026 (MM-YYYY format)",
                "2026/01 (YYYY/MM format)",
                "January 2026 (Month Year)",
                "Jan 2026 (Month abbr Year)",
            ],
            "examples": ["2026-01", "January 2026", "Jan 2026"],
        },
    )


# ============================================================================
# Error Adaptation (Convert Exceptions to Clear Messages)
# ============================================================================


def adapt_subscription_error(error: Exception, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Convert billing exception to clear error response with recovery hints.

    Parameters
    ----------
    error : Exception
        The exception from runtime operations.
    context : dict, optional
        Additional context about the operation.

    Returns
    -------
    dict
        Error response with clear message and recovery hints.
    """
    from specify_cli.runtime.billing_exceptions import (
        BillingException,
        InvoiceAlreadyExists,
        SubscriptionNotActive,
        SubscriptionNotFound,
        UsageTrackingFailed,
    )

    context = context or {}

    # Handle known billing exceptions
    if isinstance(error, SubscriptionNotActive):
        user_id = error.context.get("user_id") or context.get("user_id")
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "recovery": [
                f"Create a subscription first: `specify billing create-subscription {user_id} --tier free`",
                "Then retry your operation",
            ],
        }

    if isinstance(error, SubscriptionNotFound):
        user_id = error.context.get("user_id") or context.get("user_id")
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "recovery": [f"No subscription found for user {user_id}", "Create one first: `specify billing create-subscription {user_id}`"],
        }

    if isinstance(error, InvalidBillingPeriod):
        accepted = error.context.get("accepted_formats", [])
        examples = error.context.get("examples", [])
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "accepted_formats": accepted,
            "examples": examples,
            "recovery": [
                f"Use format: YYYY-MM (e.g., {examples[0] if examples else '2026-01'})",
                f"Or say: 'January 2026' format",
            ],
        }

    if isinstance(error, InvoiceAlreadyExists):
        period = error.context.get("billing_period")
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "invoice_id": error.context.get("invoice_id"),
            "recovery": [
                f"Invoice already generated for period {period}",
                f"Try next month: Use period {_get_next_month(period)}" if period else "Try a different period",
            ],
        }

    if isinstance(error, UsageTrackingFailed):
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "recovery": ["Check that subscription is still active", "Retry the operation"],
        }

    if isinstance(error, BillingException):
        # Generic billing exception
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "context": error.context if error.context else None,
        }

    # Unknown exception - log and return generic error
    return {
        "success": False,
        "error": f"Unexpected error: {str(error)}",
        "error_code": "INTERNAL_ERROR",
        "recovery": ["Contact support if this persists"],
    }


# ============================================================================
# Pre-Condition Validators
# ============================================================================


def validate_user_id(user_id: int | str) -> int:
    """Validate and normalize user ID.

    Parameters
    ----------
    user_id : int or str
        User ID.

    Returns
    -------
    int
        Validated user ID.

    Raises
    ------
    ValueError
        If user ID invalid.
    """
    try:
        uid = int(user_id)
        if uid < 0:
            raise ValueError("User ID must be non-negative")
        return uid
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid user ID: {user_id}") from e


def validate_amount(amount: float | int) -> float:
    """Validate usage amount.

    Parameters
    ----------
    amount : float or int
        Amount consumed.

    Returns
    -------
    float
        Validated amount.

    Raises
    ------
    ValueError
        If amount invalid.
    """
    try:
        amt = float(amount)
        if amt < 0:
            # Negative amounts allowed as credits
            return amt
        return amt
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid amount: {amount}") from e


# ============================================================================
# Helpers
# ============================================================================


def _get_next_month(billing_period: str) -> str:
    """Get next month in YYYY-MM format.

    Parameters
    ----------
    billing_period : str
        Current period in YYYY-MM format.

    Returns
    -------
    str
        Next period in YYYY-MM format.
    """
    try:
        parsed = datetime.strptime(billing_period, "%Y-%m")
        if parsed.month == 12:
            next_month = parsed.replace(year=parsed.year + 1, month=1)
        else:
            next_month = parsed.replace(month=parsed.month + 1)
        return next_month.strftime("%Y-%m")
    except ValueError:
        return "next month"
