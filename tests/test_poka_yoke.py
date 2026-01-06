"""
Test Suite: Poka Yoke Mistake-Proofing Mechanisms
=================================================

Tests validate that Poka Yoke prevents MCP agent confusion.
Chicago-style: aggressive tests designed to break the system.
"""

from __future__ import annotations

import pytest
from specify_cli.runtime.billing_poka_yoke import (
    validate_and_suggest_tier,
    parse_billing_period,
    adapt_subscription_error,
    validate_user_id,
    validate_amount,
)
from specify_cli.runtime.billing_exceptions import (
    InvalidSubscriptionTier,
    InvalidBillingPeriod,
    SubscriptionNotActive,
    InvoiceAlreadyExists,
)


# ============================================================================
# POKA YOKE TEST CLASS 1: Tier Validation & Suggestions
# ============================================================================


class TestTierValidationPretection:
    """Poka Yoke: Prevent invalid tier input."""

    def test_valid_tiers_accepted(self):
        """Valid tiers should be accepted without suggestion."""
        assert validate_and_suggest_tier("free") == ("free", None)
        assert validate_and_suggest_tier("professional") == ("professional", None)
        assert validate_and_suggest_tier("enterprise") == ("enterprise", None)

    def test_case_insensitive_validation(self):
        """Tier validation should be case-insensitive."""
        assert validate_and_suggest_tier("FREE") == ("free", None)
        assert validate_and_suggest_tier("PROFESSIONAL") == ("professional", None)
        assert validate_and_suggest_tier("Enterprise") == ("enterprise", None)

    def test_common_mistakes_suggest_correction(self):
        """Common mistakes should suggest correct tier."""
        assert validate_and_suggest_tier("standard") == ("professional", "professional")
        assert validate_and_suggest_tier("pro") == ("professional", "professional")
        assert validate_and_suggest_tier("basic") == ("free", "free")
        assert validate_and_suggest_tier("premium") == ("enterprise", "enterprise")
        assert validate_and_suggest_tier("gold") == ("enterprise", "enterprise")

    def test_fuzzy_match_suggestions(self):
        """Fuzzy match should suggest close matches."""
        # "fre" is close to "free"
        validated, suggestion = validate_and_suggest_tier("fre")
        assert suggestion is not None  # Should suggest something

    def test_completely_invalid_tier_raises(self):
        """Completely invalid tier should raise with context."""
        with pytest.raises(InvalidSubscriptionTier) as exc_info:
            validate_and_suggest_tier("platinum_mega_tier")

        error = exc_info.value
        assert "platinum_mega_tier" in error.message
        assert error.error_code == "UNRECOGNIZED_TIER"
        assert "valid_options" in error.context
        # Check all valid options are present (order may vary)
        assert set(error.context["valid_options"]) == {"free", "professional", "enterprise"}


# ============================================================================
# POKA YOKE TEST CLASS 2: Billing Period Parsing
# ============================================================================


class TestBillingPeriodParsingProtection:
    """Poka Yoke: Prevent billing period format errors."""

    def test_parse_standard_format(self):
        """Standard YYYY-MM format should parse."""
        assert parse_billing_period("2026-01") == "2026-01"
        assert parse_billing_period("2026-12") == "2026-12"
        assert parse_billing_period("2025-06") == "2025-06"

    def test_parse_reversed_format(self):
        """Reversed MM-YYYY format should parse."""
        assert parse_billing_period("01-2026") == "2026-01"
        assert parse_billing_period("12-2026") == "2026-12"

    def test_parse_slash_format(self):
        """Slash formats should parse."""
        assert parse_billing_period("2026/01") == "2026-01"
        assert parse_billing_period("01/2026") == "2026-01"

    def test_parse_full_month_name(self):
        """Full month names should parse."""
        assert parse_billing_period("January 2026") == "2026-01"
        assert parse_billing_period("February 2026") == "2026-02"
        assert parse_billing_period("December 2026") == "2026-12"

    def test_parse_month_abbreviation(self):
        """Month abbreviations should parse."""
        assert parse_billing_period("Jan 2026") == "2026-01"
        assert parse_billing_period("Feb 2026") == "2026-02"
        assert parse_billing_period("Dec 2026") == "2026-12"

    def test_parse_reversed_month_name(self):
        """Reversed month name format should parse."""
        assert parse_billing_period("2026 January") == "2026-01"
        assert parse_billing_period("2026 December") == "2026-12"

    def test_parse_single_digit_month(self):
        """Single digit months should normalize to two digits."""
        assert parse_billing_period("2026-1") == "2026-01"
        assert parse_billing_period("2026-9") == "2026-09"

    def test_invalid_month_raises(self):
        """Month outside 1-12 should raise."""
        with pytest.raises(InvalidBillingPeriod) as exc_info:
            parse_billing_period("2026-13")

        assert exc_info.value.error_code == "INVALID_MONTH"
        assert "13" in exc_info.value.message

    def test_invalid_format_suggests_valid(self):
        """Invalid format should suggest valid formats."""
        with pytest.raises(InvalidBillingPeriod) as exc_info:
            parse_billing_period("January-2026")

        error = exc_info.value
        assert error.error_code == "INVALID_PERIOD_FORMAT"
        assert "accepted_formats" in error.context
        assert "examples" in error.context


# ============================================================================
# POKA YOKE TEST CLASS 3: Error Adaptation
# ============================================================================


class TestErrorAdaptationProtection:
    """Poka Yoke: Convert exceptions to clear error messages."""

    def test_subscription_not_active_error(self):
        """SubscriptionNotActive should adapt to clear error with recovery."""
        error = SubscriptionNotActive(
            "Cannot track usage: user 123 has no active subscription",
            error_code="NO_ACTIVE_SUBSCRIPTION",
            context={"user_id": 123},
        )

        adapted = adapt_subscription_error(error)

        assert adapted["success"] is False
        assert "error" in adapted
        assert "recovery" in adapted
        assert "recovery" in adapted
        assert len(adapted["recovery"]) > 0
        # Recovery should suggest how to create subscription
        assert any("create" in str(r).lower() for r in adapted["recovery"])

    def test_invalid_billing_period_error(self):
        """InvalidBillingPeriod should adapt with examples."""
        error = InvalidBillingPeriod(
            "Cannot parse billing period: 'January-2026'",
            error_code="INVALID_PERIOD_FORMAT",
            context={
                "provided": "January-2026",
                "accepted_formats": ["2026-01", "January 2026", "Jan 2026"],
                "examples": ["2026-01"],
            },
        )

        adapted = adapt_subscription_error(error)

        assert adapted["success"] is False
        assert "accepted_formats" in adapted
        assert "examples" in adapted
        assert "recovery" in adapted
        # Recovery should show correct format
        assert any("YYYY-MM" in str(r) for r in adapted["recovery"])

    def test_invoice_already_exists_error(self):
        """InvoiceAlreadyExists should suggest next month."""
        error = InvoiceAlreadyExists(
            "Invoice already exists for user 123 in period 2026-01",
            error_code="DUPLICATE_INVOICE",
            context={
                "user_id": 123,
                "billing_period": "2026-01",
                "invoice_id": "inv_123",
            },
        )

        adapted = adapt_subscription_error(error)

        assert adapted["success"] is False
        assert "invoice_id" in adapted
        assert "recovery" in adapted
        # Recovery should suggest next month
        assert any("2026-02" in str(r) for r in adapted["recovery"])

    def test_adapted_errors_always_have_recovery(self):
        """All adapted errors should have recovery hints."""
        errors = [
            SubscriptionNotActive("No sub", error_code="NO_SUB", context={"user_id": 1}),
            InvalidBillingPeriod("Bad date", error_code="BAD_DATE", context={}),
            InvoiceAlreadyExists(
                "Dup invoice",
                error_code="DUP",
                context={"billing_period": "2026-01", "user_id": 1},
            ),
        ]

        for error in errors:
            adapted = adapt_subscription_error(error)
            assert adapted["success"] is False
            assert "recovery" in adapted
            assert isinstance(adapted["recovery"], list)
            assert len(adapted["recovery"]) > 0


# ============================================================================
# POKA YOKE TEST CLASS 4: Input Validation
# ============================================================================


class TestInputValidationProtection:
    """Poka Yoke: Validate user inputs before operations."""

    def test_validate_user_id_integer(self):
        """User ID as integer should validate."""
        assert validate_user_id(123) == 123
        assert validate_user_id(1) == 1
        assert validate_user_id(2**31 - 1) == 2**31 - 1

    def test_validate_user_id_string_integer(self):
        """User ID as string should convert."""
        assert validate_user_id("123") == 123
        assert validate_user_id("1") == 1

    def test_validate_user_id_negative_rejected(self):
        """Negative user ID should be rejected."""
        with pytest.raises(ValueError):
            validate_user_id(-1)

    def test_validate_user_id_non_numeric_rejected(self):
        """Non-numeric user ID should be rejected."""
        with pytest.raises(ValueError):
            validate_user_id("not_a_number")

    def test_validate_amount_positive(self):
        """Positive amounts should validate."""
        assert validate_amount(50) == 50.0
        assert validate_amount(50.5) == 50.5
        assert validate_amount("100") == 100.0

    def test_validate_amount_zero_allowed(self):
        """Zero amount should be allowed."""
        assert validate_amount(0) == 0.0

    def test_validate_amount_negative_allowed_as_credit(self):
        """Negative amounts allowed as credits."""
        assert validate_amount(-50) == -50.0

    def test_validate_amount_non_numeric_rejected(self):
        """Non-numeric amounts should be rejected."""
        with pytest.raises(ValueError):
            validate_amount("not_a_number")


# ============================================================================
# POKA YOKE TEST CLASS 5: Integration Tests
# ============================================================================


class TestPokaYokeIntegration:
    """Poka Yoke: End-to-end mistake prevention."""

    def test_confused_user_typos_corrected(self):
        """System should guide confused user through typos."""
        # User says "standard tier"
        corrected_tier, suggestion = validate_and_suggest_tier("standard")
        assert corrected_tier == "professional"
        assert suggestion == "professional"

        # User says "Jan 2026" instead of "2026-01"
        period = parse_billing_period("Jan 2026")
        assert period == "2026-01"

    def test_multiple_format_variations_all_work(self):
        """System should accept all reasonable input formats."""
        formats = [
            ("2026-01", "2026-01"),
            ("01-2026", "2026-01"),
            ("2026/01", "2026-01"),
            ("January 2026", "2026-01"),
            ("Jan 2026", "2026-01"),
        ]

        for user_input, expected in formats:
            assert parse_billing_period(user_input) == expected

    def test_error_never_leaves_user_stranded(self):
        """All errors should provide clear recovery path."""
        test_errors = [
            SubscriptionNotActive(
                "No subscription",
                error_code="NO_SUB",
                context={"user_id": 123},
            ),
            InvalidBillingPeriod(
                "Bad date",
                error_code="BAD_DATE",
                context={
                    "provided": "bad",
                    "accepted_formats": ["YYYY-MM"],
                    "examples": ["2026-01"],
                },
            ),
        ]

        for error in test_errors:
            adapted = adapt_subscription_error(error)
            assert adapted["success"] is False
            assert "error" in adapted
            assert "recovery" in adapted
            # Each recovery item should be actionable
            for recovery in adapted["recovery"]:
                assert len(str(recovery)) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
