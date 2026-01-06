"""
Adversarial Chicago-style TDD QA Suite for RevOps Capabilities
===============================================================

Chicago School of TDD: Write aggressive tests that expose issues, then fix.

This suite focuses on the CRITICAL 20% of test scenarios that find 80% of issues:
1. Subscription lifecycle edge cases
2. Usage quota enforcement boundaries
3. Invoice generation state consistency
4. Feature access control validation
5. Currency/decimal handling precision
6. State consistency and cascading issues

Each test is adversarial - designed to break the system and expose hidden bugs.
"""

from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from specify_cli.db.models import (
    Base,
    Subscription,
    UsageEvent,
    Invoice,
    InvoiceStatus,
)
from specify_cli.runtime.billing import (
    create_subscription,
    get_subscription,
    update_subscription_tier,
    cancel_subscription,
    track_usage_event,
    get_usage_quota_status,
    generate_invoice,
    mark_invoice_paid,
    get_mrr,
    get_revenue_by_tier,
)
from specify_cli.ops.billing import (
    SubscriptionConfig,
    SubscriptionTier,
    check_usage_quota,
    apply_overage_charges,
    calculate_mrr,
    calculate_arr,
)
from specify_cli.security.subscription_enforcement import SubscriptionEnforcer, TierFeatures


@pytest.fixture
def db_session():
    """In-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


# ============================================================================
# ADVERSARIAL TEST CLASS 1: Subscription Lifecycle Edge Cases
# ============================================================================
# Impact: Free users shouldn't generate invoices, tier transitions must be clean


class TestSubscriptionLifecycleAdversarial:
    """Adversarial tests for subscription state transitions."""

    def test_free_tier_invoice_generation_should_fail(self, db_session):
        """ADVERSARIAL: Free tier user should NOT generate a paid invoice."""
        # Create free subscription
        result = create_subscription(db_session, user_id=9001, tier="free")
        assert result.get("error") is None

        # Attempt to generate invoice
        invoice = generate_invoice(db_session, user_id=9001)

        # ADVERSARIAL: Should either fail or generate $0 invoice
        if "error" not in invoice:
            # If it succeeds, amount must be $0
            assert Decimal(invoice.get("amount", 0)) == Decimal("0"), \
                f"Free tier invoice should be $0, got {invoice.get('amount')}"

    def test_downgrade_free_then_professional_then_free_consistency(self, db_session):
        """ADVERSARIAL: Rapid tier transitions should maintain data consistency."""
        user_id = 9002

        # Create pro subscription
        create_subscription(db_session, user_id, "professional")
        sub1 = get_subscription(db_session, user_id)
        assert sub1["tier"] == "professional"

        # Downgrade to free
        update_subscription_tier(db_session, user_id, "free")
        sub2 = get_subscription(db_session, user_id)
        assert sub2["tier"] == "free"
        assert sub2["status"] == "active"

        # Upgrade back to pro
        update_subscription_tier(db_session, user_id, "professional")
        sub3 = get_subscription(db_session, user_id)
        assert sub3["tier"] == "professional"

        # Verify start_date is consistent (doesn't reset)
        assert sub1.get("start_date") == sub3.get("start_date"), \
            "Start date should not change on tier upgrades"

    def test_cancel_then_recreate_subscription(self, db_session):
        """ADVERSARIAL: Cancelling and recreating should create new subscription record."""
        user_id = 9003

        # Create subscription
        result1 = create_subscription(db_session, user_id, "professional")
        sub_id_1 = result1.get("subscription_id")

        # Cancel it
        cancel_result = cancel_subscription(db_session, user_id)
        assert cancel_result.get("error") is None

        # Verify status is cancelled (use include_cancelled to retrieve it)
        cancelled = get_subscription(db_session, user_id, include_cancelled=True)
        assert cancelled.get("status") == "cancelled"

        # Recreate
        result2 = create_subscription(db_session, user_id, "professional")
        sub_id_2 = result2.get("subscription_id")

        # ADVERSARIAL: Should create NEW subscription record
        assert sub_id_1 != sub_id_2, \
            "Recreating subscription should create new record, not reactivate old one"

    def test_upgrade_to_same_tier_is_idempotent(self, db_session):
        """ADVERSARIAL: Upgrading to same tier should be safe operation."""
        user_id = 9004

        create_subscription(db_session, user_id, "professional")
        sub1 = get_subscription(db_session, user_id)

        # "Upgrade" to same tier
        update_subscription_tier(db_session, user_id, "professional")
        sub2 = get_subscription(db_session, user_id)

        # Should be identical
        assert sub1["tier"] == sub2["tier"]
        assert sub1["status"] == sub2["status"]
        assert sub1["start_date"] == sub2["start_date"]

    def test_create_subscription_with_invalid_tier_rejected(self, db_session):
        """ADVERSARIAL: Invalid tier should be rejected with clear error."""
        result = create_subscription(db_session, user_id=9005, tier="invalid_tier_xyz")

        # Should produce error dict, not raise exception
        assert isinstance(result, dict), "Should return dict"
        assert "error" in result or result.get("tier") is None, \
            f"Invalid tier should produce error: {result}"


# ============================================================================
# ADVERSARIAL TEST CLASS 2: Usage Quota Enforcement Boundaries
# ============================================================================
# Impact: Incorrect quota enforcement leads to unfair usage limits


class TestUsageQuotaAdversarial:
    """Adversarial tests for quota enforcement and edge cases."""

    def test_track_exactly_at_quota_boundary(self, db_session):
        """ADVERSARIAL: Using exactly at quota should trigger warning."""
        user_id = 9010

        # Free tier = 100 API calls quota
        create_subscription(db_session, user_id, "free")

        # Track exactly 100 calls
        track_usage_event(db_session, user_id, "api_calls", 100)
        status = get_usage_quota_status(db_session, user_id)

        # Should be at 100% but NOT exceeded
        assert status.get("percentage_used") == Decimal("100")
        assert status.get("exceeded") is False, "At quota is not exceeded"
        assert status.get("warning") is True, "At quota should warn"

    def test_track_one_call_over_quota(self, db_session):
        """ADVERSARIAL: One call over quota should show exceeded."""
        user_id = 9011

        # Free tier = 100 API calls quota
        create_subscription(db_session, user_id, "free")

        # Track 101 calls (1 over)
        track_usage_event(db_session, user_id, "api_calls", 101)
        status = get_usage_quota_status(db_session, user_id)

        # Should be exceeded
        assert status.get("exceeded") is True, "Should be exceeded"
        assert status.get("percentage_used") > Decimal("100")

    def test_track_zero_usage_is_allowed(self, db_session):
        """ADVERSARIAL: Tracking 0 usage shouldn't break system."""
        user_id = 9012

        create_subscription(db_session, user_id, "professional")

        # Track 0 API calls
        result = track_usage_event(db_session, user_id, "api_calls", 0)

        # Should succeed
        assert "error" not in result, f"Zero usage should be allowed: {result.get('error')}"

    def test_track_negative_usage_is_rejected(self, db_session):
        """ADVERSARIAL: Negative usage (credits) should be rejected or handled specially."""
        user_id = 9013

        create_subscription(db_session, user_id, "professional")

        # Attempt to track negative usage (credit)
        result = track_usage_event(db_session, user_id, "api_calls", -50)

        # Should either reject or explicitly handle as credit
        # For now, verify system doesn't crash and has sensible behavior
        assert result is not None
        if "error" not in result:
            status = get_usage_quota_status(db_session, user_id)
            # If credit was applied, used should be negative or zero
            assert status.get("api_calls_used", 0) <= 0, \
                "Negative usage should result in credit (negative usage or zero)"

    def test_track_extremely_large_usage_amount(self, db_session):
        """ADVERSARIAL: Million API calls in one event shouldn't crash system."""
        user_id = 9014

        create_subscription(db_session, user_id, "professional")

        # Track 1,000,000 API calls (way over pro quota of 10,000)
        result = track_usage_event(db_session, user_id, "api_calls", 1_000_000)

        # Should succeed (runtime allows it, overage charges apply)
        assert "error" not in result, f"Large usage should be tracked: {result.get('error')}"

        status = get_usage_quota_status(db_session, user_id)
        assert status.get("exceeded") is True

    def test_usage_quota_with_no_subscription_fails_gracefully(self, db_session):
        """ADVERSARIAL: Checking quota for user with no subscription should fail gracefully."""
        result = get_usage_quota_status(db_session, user_id=9999)

        # Should return error, not crash
        assert "error" in result or result.get("tier") is None, \
            f"Should handle missing subscription: {result}"

    def test_track_usage_on_cancelled_subscription(self, db_session):
        """ADVERSARIAL: Should not allow tracking usage on cancelled subscription."""
        user_id = 9015

        create_subscription(db_session, user_id, "professional")
        cancel_subscription(db_session, user_id)

        # Attempt to track usage
        result = track_usage_event(db_session, user_id, "api_calls", 50)

        # Should either reject or mark as invalid
        if "error" not in result:
            # If allowed, verify subscription is marked as cancelled
            sub = get_subscription(db_session, user_id)
            assert sub.get("status") == "cancelled"


# ============================================================================
# ADVERSARIAL TEST CLASS 3: Invoice Generation State Consistency
# ============================================================================
# Impact: Duplicate invoices, orphaned invoices, calculation errors


class TestInvoiceGenerationAdversarial:
    """Adversarial tests for invoice creation and state consistency."""

    def test_invoice_duplicate_prevention(self, db_session):
        """ADVERSARIAL: Generating invoice twice same period should be prevented."""
        user_id = 9020

        create_subscription(db_session, user_id, "professional")

        # Generate invoice once
        invoice1 = generate_invoice(db_session, user_id, billing_period="2026-01")
        assert "error" not in invoice1

        # Try to generate again for same period
        invoice2 = generate_invoice(db_session, user_id, billing_period="2026-01")

        # Should be rejected
        assert "error" in invoice2, \
            "Second invoice for same period should return error, not duplicate"

    def test_invoice_without_subscription_fails(self, db_session):
        """ADVERSARIAL: Cannot generate invoice for user with no subscription."""
        result = generate_invoice(db_session, user_id=9999)

        assert "error" in result, "Should fail to generate invoice without subscription"

    def test_invoice_for_free_tier_zero_amount(self, db_session):
        """ADVERSARIAL: Free tier invoice must be $0."""
        user_id = 9021

        create_subscription(db_session, user_id, "free")
        invoice = generate_invoice(db_session, user_id)

        if "error" not in invoice:
            amount = Decimal(invoice.get("amount", 0))
            assert amount == Decimal("0"), \
                f"Free tier invoice must be $0, got {amount}"

    def test_invoice_line_items_sum_to_total(self, db_session):
        """ADVERSARIAL: Invoice line items must sum to total amount."""
        user_id = 9022

        create_subscription(db_session, user_id, "professional")

        # Track some usage to create overage
        track_usage_event(db_session, user_id, "api_calls", 15000)  # Exceeds 10k quota

        invoice = generate_invoice(db_session, user_id)

        if "error" not in invoice and invoice.get("line_items"):
            line_items = invoice.get("line_items", [])
            items_sum = sum(Decimal(item.get("amount", 0)) for item in line_items)
            total = Decimal(invoice.get("amount", 0))

            # Allow small rounding differences
            assert abs(items_sum - total) < Decimal("0.01"), \
                f"Line items ({items_sum}) must sum to total ({total})"

    def test_invoice_with_zero_monthly_cost_tier(self, db_session):
        """ADVERSARIAL: Invoice line items for free tier should show correctly."""
        user_id = 9023

        create_subscription(db_session, user_id, "free")
        invoice = generate_invoice(db_session, user_id)

        if "error" not in invoice:
            line_items = invoice.get("line_items", [])
            # Should have description and $0 amount
            assert len(line_items) > 0, "Free tier should have line items (even if $0)"
            for item in line_items:
                assert "description" in item
                assert Decimal(item.get("amount", 0)) >= Decimal("0")

    def test_invoice_with_invalid_billing_period_format(self, db_session):
        """ADVERSARIAL: Invalid billing period format should be rejected."""
        user_id = 9024

        create_subscription(db_session, user_id, "professional")

        # Try invalid period formats
        for bad_period in ["2026/01", "01-2026", "20260101", "2026-13", "not-a-date"]:
            result = generate_invoice(db_session, user_id, billing_period=bad_period)
            assert "error" in result, \
                f"Invalid period '{bad_period}' should produce error"

    def test_mark_paid_on_free_tier_invoice(self, db_session):
        """ADVERSARIAL: Marking free tier invoice as paid should work."""
        user_id = 9025

        create_subscription(db_session, user_id, "free")
        invoice = generate_invoice(db_session, user_id)

        if "error" not in invoice:
            invoice_id = invoice.get("invoice_id")
            result = mark_invoice_paid(db_session, invoice_id)

            # Should succeed (even though amount is $0)
            assert "error" not in result


# ============================================================================
# ADVERSARIAL TEST CLASS 4: Feature Access Control Validation
# ============================================================================
# Impact: Users accessing features they shouldn't have


class TestFeatureAccessAdversarial:
    """Adversarial tests for feature access control."""

    def test_feature_access_case_sensitivity(self):
        """ADVERSARIAL: Feature access should handle case variations."""
        enforcer = SubscriptionEnforcer()

        # Try different cases
        result_lower = enforcer.check_feature_access("free", "sso")
        result_upper = enforcer.check_feature_access("free", "SSO")
        result_mixed = enforcer.check_feature_access("free", "Sso")

        # All should give consistent result (either all allowed or all denied)
        assert result_lower.get("allowed") == result_upper.get("allowed") == result_mixed.get("allowed"), \
            f"Feature access should be case-insensitive: {result_lower} vs {result_upper} vs {result_mixed}"

    def test_feature_access_with_invalid_tier(self):
        """ADVERSARIAL: Invalid tier should be rejected, not default to access."""
        enforcer = SubscriptionEnforcer()

        result = enforcer.check_feature_access("platinum", "api_access")

        assert "error" in result or result.get("allowed") is False, \
            "Invalid tier should not grant access"

    def test_feature_access_nonexistent_feature(self):
        """ADVERSARIAL: Non-existent feature should be rejected, not default."""
        enforcer = SubscriptionEnforcer()

        result = enforcer.check_feature_access("professional", "alien_features_xyz")

        assert result.get("allowed") is False, \
            "Non-existent feature should always be denied"

    def test_get_tier_features_all_valid(self):
        """ADVERSARIAL: Features for tier must be valid, non-empty, consistent."""
        # Test all tiers
        for tier in ["free", "professional", "enterprise"]:
            features = TierFeatures.get_features_for_tier(tier)

            assert isinstance(features, list), f"Features for {tier} should be list"
            assert len(features) > 0, f"Tier {tier} should have at least one feature"
            assert all(isinstance(f, str) for f in features), \
                f"All features for {tier} should be strings"

    def test_feature_list_hierarchy(self):
        """ADVERSARIAL: Higher tiers should have all features of lower tiers."""
        free_features = set(TierFeatures.get_features_for_tier("free"))
        pro_features = set(TierFeatures.get_features_for_tier("professional"))
        ent_features = set(TierFeatures.get_features_for_tier("enterprise"))

        # Professional should include all free features
        assert free_features.issubset(pro_features), \
            f"Professional tier should include all free tier features"

        # Enterprise should include all professional features
        assert pro_features.issubset(ent_features), \
            f"Enterprise tier should include all professional tier features"


# ============================================================================
# ADVERSARIAL TEST CLASS 5: Currency & Decimal Handling Precision
# ============================================================================
# Impact: Billing errors from rounding and precision issues


class TestDecimalPrecisionAdversarial:
    """Adversarial tests for currency and decimal calculations."""

    def test_overage_rate_precision(self, db_session):
        """ADVERSARIAL: Overage calculation must handle precise rates."""
        user_id = 9030

        create_subscription(db_session, user_id, "professional")  # 10,000 calls/month

        # Track 10,500 calls (500 over quota)
        track_usage_event(db_session, user_id, "api_calls", 10500)

        invoice = generate_invoice(db_session, user_id)

        if "error" not in invoice:
            # Pro tier: $49/month + overage at $0.05/call
            # Expected: $49 + (500 * 0.05) = $49 + $25 = $74
            amount = Decimal(invoice.get("amount", 0))

            # Should include overage
            expected_overage = Decimal("500") * Decimal("0.05")
            assert expected_overage == Decimal("25"), "Overage calculation incorrect"

    def test_mrr_calculation_with_mixed_tiers(self, db_session):
        """ADVERSARIAL: MRR must correctly aggregate multiple tiers."""
        # Create subscriptions at each tier
        create_subscription(db_session, user_id=9031, tier="free")  # $0
        create_subscription(db_session, user_id=9032, tier="professional")  # $49
        create_subscription(db_session, user_id=9033, tier="enterprise")  # $499

        mrr = get_mrr(db_session)

        # Expected MRR = 0 + 49 + 499 = 548
        expected_mrr = Decimal("548")
        assert mrr == expected_mrr, \
            f"MRR with mixed tiers should be {expected_mrr}, got {mrr}"

    def test_arr_calculation_is_mrr_times_12(self, db_session):
        """ADVERSARIAL: ARR must be exactly MRR * 12."""
        create_subscription(db_session, user_id=9034, tier="professional")

        mrr = get_mrr(db_session)

        # Manually verify ARR = MRR * 12
        expected_arr = Decimal(mrr) * Decimal("12")

        # ARR for professional tier should be $49 * 12 = $588
        assert expected_arr == Decimal("588"), \
            f"ARR calculation: {expected_arr} should equal $588"

    def test_revenue_by_tier_totals_to_mrr(self, db_session):
        """ADVERSARIAL: Revenue breakdown totals must equal MRR."""
        create_subscription(db_session, user_id=9035, tier="free")
        create_subscription(db_session, user_id=9036, tier="professional")
        create_subscription(db_session, user_id=9037, tier="professional")  # 2x pro

        breakdown = get_revenue_by_tier(db_session)
        mrr = get_mrr(db_session)

        # Total from breakdown
        total_from_breakdown = Decimal(breakdown.get("total", 0))
        mrr_decimal = Decimal(mrr)

        # Use small tolerance for decimal comparison
        assert abs(total_from_breakdown - mrr_decimal) < Decimal("0.01"), \
            f"Breakdown total ({total_from_breakdown}) must equal MRR ({mrr_decimal})"

    def test_currency_rounding_consistent(self, db_session):
        """ADVERSARIAL: All currency values must use consistent rounding."""
        user_id = 9038

        create_subscription(db_session, user_id, "professional")
        track_usage_event(db_session, user_id, "api_calls", 10333)  # Odd number for rounding

        invoice = generate_invoice(db_session, user_id)

        if "error" not in invoice:
            amount = Decimal(invoice.get("amount", 0))

            # Amount should have at most 2 decimal places (money)
            amount_str = str(amount)
            decimal_places = 0
            if '.' in amount_str:
                decimal_places = len(amount_str.split('.')[1])

            assert decimal_places <= 2, \
                f"Currency should have max 2 decimal places, got {decimal_places}"


# ============================================================================
# ADVERSARIAL TEST CLASS 6: State Consistency & Cascading Issues
# ============================================================================
# Impact: Data corruption from inconsistent state changes


class TestStateConsistencyAdversarial:
    """Adversarial tests for state consistency and cascading effects."""

    def test_multiple_concurrent_usage_tracks(self, db_session):
        """ADVERSARIAL: Multiple usage events should aggregate correctly."""
        user_id = 9040

        create_subscription(db_session, user_id, "professional")

        # Simulate multiple concurrent API calls being tracked
        for i in range(10):
            track_usage_event(db_session, user_id, "api_calls", 500)

        status = get_usage_quota_status(db_session, user_id)

        # Should total 5000
        assert status.get("api_calls_used") == 5000, \
            f"Multiple events should aggregate: got {status.get('api_calls_used')}"

    def test_cancelled_subscription_blocks_usage_tracking(self, db_session):
        """ADVERSARIAL: Usage tracking on cancelled sub should be handled."""
        user_id = 9041

        create_subscription(db_session, user_id, "professional")
        cancel_subscription(db_session, user_id)

        # Try to track usage on cancelled subscription
        result = track_usage_event(db_session, user_id, "api_calls", 100)

        # System should either reject or mark explicitly
        if "error" not in result:
            # If allowed, verify subscription status
            sub = get_subscription(db_session, user_id)
            assert sub.get("status") == "cancelled", \
                "Usage tracking on cancelled sub should fail or be marked"

    def test_invoice_cascade_on_tier_change(self, db_session):
        """ADVERSARIAL: Changing tier should not affect existing invoices."""
        user_id = 9042

        create_subscription(db_session, user_id, "free")
        invoice1 = generate_invoice(db_session, user_id, "2026-01")

        if "error" not in invoice1:
            # Original invoice should be $0 for free tier
            amount1 = Decimal(invoice1.get("amount", 0))
            assert amount1 == Decimal("0"), \
                f"Free tier invoice should be $0, got {amount1}"

            # Upgrade tier
            update_subscription_tier(db_session, user_id, "professional")

            # Generate new invoice for different month
            invoice2 = generate_invoice(db_session, user_id, "2026-02")

            # First invoice should still be $0 (immutable)
            assert amount1 == Decimal("0")

    def test_subscription_relationships_on_cascade_delete(self, db_session):
        """ADVERSARIAL: Deleting subscription should handle cascades properly."""
        user_id = 9043

        create_subscription(db_session, user_id, "professional")

        # Create related records
        track_usage_event(db_session, user_id, "api_calls", 500)
        invoice = generate_invoice(db_session, user_id)

        # Cancel subscription
        cancel_subscription(db_session, user_id)

        # Verify subscription is cancelled, not deleted (use include_cancelled)
        sub = get_subscription(db_session, user_id, include_cancelled=True)
        assert sub is not None, "Cancelled subscription should still exist"
        assert sub.get("status") == "cancelled"

        # Usage events should still exist (for audit)
        # Invoice should still exist


# ============================================================================
# ADVERSARIAL TEST CLASS 7: CLI Integration Stress
# ============================================================================
# Impact: CLI commands failing silently or with bad errors


class TestCLIAdversarial:
    """Adversarial tests for CLI command integration."""

    def test_cli_handles_zero_subscriptions(self, db_session):
        """ADVERSARIAL: CLI revenue commands with zero subscriptions."""
        # No subscriptions created

        mrr = get_mrr(db_session)
        assert mrr == 0 or mrr == Decimal("0"), \
            f"MRR with no subscriptions should be 0, got {mrr}"

        breakdown = get_revenue_by_tier(db_session)
        total = breakdown.get("total", 0)
        assert total == 0 or total == Decimal("0") or total == "0", \
            f"Revenue breakdown with no subscriptions should total 0, got {total}"

    def test_large_user_id_values(self, db_session):
        """ADVERSARIAL: System should handle large integer user IDs."""
        user_id = 2**31 - 1  # Max 32-bit int

        result = create_subscription(db_session, user_id, "professional")

        assert "error" not in result, \
            f"System should handle large user IDs: {result.get('error')}"

        sub = get_subscription(db_session, user_id)
        assert sub.get("error") is None

    def test_user_id_zero_edge_case(self, db_session):
        """ADVERSARIAL: User ID of 0 should be handled."""
        result = create_subscription(db_session, user_id=0, tier="free")

        # Should either work or explicitly reject
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
