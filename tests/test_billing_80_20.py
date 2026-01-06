"""
tests.test_billing_80_20 - 80/20 RevOps Implementation Tests
============================================================

Tests for core billing functionality:
- Subscription management (create, upgrade, downgrade, cancel)
- Usage tracking and aggregation
- Quota enforcement
- Invoice generation
- Feature access control
- End-to-end billing workflows

Run with: pytest tests/test_billing_80_20.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from specify_cli.db.models import (
    Base,
    Invoice,
    InvoiceStatus,
    Subscription,
    SubscriptionTier,
    User,
    UsageEvent,
)
from specify_cli.ops.billing import (
    SubscriptionConfig,
    aggregate_usage_by_period,
    apply_overage_charges,
    generate_invoice_line_items,
    calculate_mrr,
    check_usage_quota,
)
from specify_cli.runtime.billing import (
    cancel_subscription,
    create_subscription,
    generate_invoice,
    get_invoices,
    get_mrr,
    get_revenue_by_tier,
    get_subscription,
    get_usage_for_period,
    get_usage_quota_status,
    mark_invoice_paid,
    track_usage_event,
    update_subscription_tier,
)
from specify_cli.security.subscription_enforcement import SubscriptionEnforcer, TierFeatures


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session_local = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session_local()

    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=b"hashed_password",
        api_key="test_api_key_123",
    )
    session.add(user)
    session.commit()

    yield session

    session.close()


@pytest.fixture
def test_user_id(db_session: Session) -> int:
    """Get test user ID."""
    user = db_session.query(User).filter(User.username == "testuser").first()
    return user.id


# ============================================================================
# Test Subscription Operations
# ============================================================================


class TestSubscriptionOperations:
    """Tests for subscription creation and management."""

    def test_create_free_subscription(self, db_session: Session, test_user_id: int) -> None:
        """Test creating a free subscription."""
        result = create_subscription(db_session, test_user_id, tier="free")

        assert result["tier"] == "free"
        assert result["status"] == "active"
        assert result["user_id"] == test_user_id
        assert result["subscription_id"]

    def test_create_professional_subscription(self, db_session: Session, test_user_id: int) -> None:
        """Test creating a professional subscription."""
        result = create_subscription(db_session, test_user_id, tier="professional")

        assert result["tier"] == "professional"
        assert result["status"] == "active"

    def test_get_subscription(self, db_session: Session, test_user_id: int) -> None:
        """Test retrieving subscription."""
        create_subscription(db_session, test_user_id, tier="professional")
        result = get_subscription(db_session, test_user_id)

        assert result is not None
        assert result["tier"] == "professional"
        assert result["api_quota"] == 10000
        assert result["storage_quota"] == 50 * 1024 * 1024 * 1024

    def test_upgrade_subscription(self, db_session: Session, test_user_id: int) -> None:
        """Test upgrading subscription tier."""
        create_subscription(db_session, test_user_id, tier="professional")
        result = update_subscription_tier(db_session, test_user_id, "enterprise")

        assert result["tier"] == "enterprise"

        # Verify in database
        sub = get_subscription(db_session, test_user_id)
        assert sub["tier"] == "enterprise"

    def test_cancel_subscription(self, db_session: Session, test_user_id: int) -> None:
        """Test cancelling subscription."""
        create_subscription(db_session, test_user_id, tier="professional")
        result = cancel_subscription(db_session, test_user_id)

        assert result["status"] == "cancelled"
        assert result["cancelled_at"]

        # Verify subscription is no longer active
        sub = get_subscription(db_session, test_user_id)
        assert sub is None


# ============================================================================
# Test Usage Tracking
# ============================================================================


class TestUsageTracking:
    """Tests for usage event tracking and aggregation."""

    def test_track_api_call(self, db_session: Session, test_user_id: int) -> None:
        """Test tracking API call usage."""
        create_subscription(db_session, test_user_id, tier="professional")

        result = track_usage_event(
            db_session,
            test_user_id,
            metric_type="api_calls",
            amount=10,
        )

        assert result["metric_type"] == "api_calls"
        assert result["amount"] == 10
        assert result["user_id"] == test_user_id
        assert result["event_id"]

    def test_track_multiple_events(self, db_session: Session, test_user_id: int) -> None:
        """Test tracking multiple usage events."""
        create_subscription(db_session, test_user_id, tier="professional")

        # Track multiple API calls
        for i in range(5):
            track_usage_event(db_session, test_user_id, "api_calls", 10)

        usage = get_usage_for_period(db_session, test_user_id)
        assert usage["api_calls"] == 50

    def test_aggregate_usage_by_period(self) -> None:
        """Test aggregating usage events."""
        events = [
            {"metric_type": "api_calls", "amount": 100, "billing_period": "2026-01"},
            {"metric_type": "api_calls", "amount": 50, "billing_period": "2026-01"},
            {"metric_type": "storage", "amount": 1000, "billing_period": "2026-01"},
        ]

        result = aggregate_usage_by_period(events, "2026-01")

        assert result["api_calls"] == 150
        assert result["storage"] == 1000

    def test_get_usage_for_period(self, db_session: Session, test_user_id: int) -> None:
        """Test retrieving usage for period."""
        create_subscription(db_session, test_user_id, tier="professional")

        track_usage_event(db_session, test_user_id, "api_calls", 100)
        track_usage_event(db_session, test_user_id, "api_calls", 50)

        usage = get_usage_for_period(db_session, test_user_id)

        assert usage["api_calls"] == 150


# ============================================================================
# Test Quota Enforcement
# ============================================================================


class TestQuotaEnforcement:
    """Tests for usage quota checking and enforcement."""

    def test_free_tier_quota(self) -> None:
        """Test free tier has 100 API calls/month."""
        config = SubscriptionConfig.get_tier_config(SubscriptionTier.FREE)
        assert config.api_quota == 100

    def test_professional_tier_quota(self) -> None:
        """Test professional tier has 10,000 API calls/month."""
        config = SubscriptionConfig.get_tier_config(SubscriptionTier.PROFESSIONAL)
        assert config.api_quota == 10000

    def test_check_quota_below_limit(self) -> None:
        """Test quota check when usage is below limit."""
        result = check_usage_quota(current_usage=50, quota=100)

        assert result["is_exceeded"] is False
        assert result["usage_percent"] == 0.5
        assert result["warning"] is False

    def test_check_quota_at_warning_threshold(self) -> None:
        """Test quota check at 80% warning threshold."""
        result = check_usage_quota(current_usage=80, quota=100, threshold_percent=0.8)

        assert result["is_exceeded"] is False
        assert result["warning"] is True

    def test_check_quota_exceeded(self) -> None:
        """Test quota check when usage exceeds limit."""
        result = check_usage_quota(current_usage=150, quota=100)

        assert result["is_exceeded"] is True
        assert result["throttled"] is True

    def test_get_quota_status(self, db_session: Session, test_user_id: int) -> None:
        """Test getting quota status for user."""
        create_subscription(db_session, test_user_id, tier="professional")
        track_usage_event(db_session, test_user_id, "api_calls", 8000)

        status = get_usage_quota_status(db_session, test_user_id)

        assert status["tier"] == "professional"
        assert status["api_quota"] == 10000
        assert status["api_calls_used"] == 8000
        assert status["remaining"] == 2000
        assert status["exceeded"] is False
        assert status["warning"] is True  # At 80%


# ============================================================================
# Test Invoicing
# ============================================================================


class TestInvoicing:
    """Tests for invoice generation and payment tracking."""

    def test_generate_invoice_no_overage(self, db_session: Session, test_user_id: int) -> None:
        """Test generating invoice with no usage overage."""
        create_subscription(db_session, test_user_id, tier="professional")
        track_usage_event(db_session, test_user_id, "api_calls", 100)

        result = generate_invoice(db_session, test_user_id)

        assert float(result["amount"]) == 49.0  # Professional tier cost
        assert result["status"] == "draft"
        assert len(result["line_items"]) == 1  # Just subscription
        assert result["invoice_id"]

    def test_generate_invoice_with_overage(self, db_session: Session, test_user_id: int) -> None:
        """Test generating invoice with usage overage charges."""
        create_subscription(db_session, test_user_id, tier="free")
        track_usage_event(db_session, test_user_id, "api_calls", 150)  # 50 over 100 quota

        result = generate_invoice(db_session, test_user_id)

        # Free tier = $0, but 50 overage * $0.05 = $2.50
        assert float(result["amount"]) == 2.50
        assert len(result["line_items"]) == 2  # Subscription + overage

    def test_get_invoices(self, db_session: Session, test_user_id: int) -> None:
        """Test retrieving user's invoices."""
        create_subscription(db_session, test_user_id, tier="professional")
        generate_invoice(db_session, test_user_id)

        invoices = get_invoices(db_session, test_user_id)

        assert len(invoices) == 1
        assert invoices[0]["status"] == "draft"

    def test_mark_invoice_paid(self, db_session: Session, test_user_id: int) -> None:
        """Test marking invoice as paid (webhook scenario)."""
        create_subscription(db_session, test_user_id, tier="professional")
        invoice_result = generate_invoice(db_session, test_user_id)
        invoice_id = invoice_result["invoice_id"]

        result = mark_invoice_paid(
            db_session,
            invoice_id,
            stripe_invoice_id="in_stripe_123",
        )

        assert result["status"] == "paid"
        assert result["paid_date"]

        # Verify in database
        invoices = get_invoices(db_session, test_user_id)
        assert invoices[0]["status"] == "paid"

    def test_invoice_line_items_calculation(self) -> None:
        """Test invoice line item generation with overages."""
        line_items, total = generate_invoice_line_items(
            SubscriptionTier.PROFESSIONAL,
            Decimal("49"),
            usage_overage={"api_calls": 100},
            overage_rate=Decimal("0.05"),
        )

        assert len(line_items) == 2
        assert line_items[0].description == "Professional Subscription"
        assert "Api Calls Overage" in line_items[1].description
        assert total == Decimal("49") + Decimal("5")  # $49 + (100 * $0.05)


# ============================================================================
# Test Feature Access Control
# ============================================================================


class TestFeatureAccessControl:
    """Tests for tier-based feature access control."""

    def test_free_tier_features(self) -> None:
        """Test free tier feature availability."""
        enforcer = SubscriptionEnforcer()

        # Check free tier has basic features
        assert TierFeatures.has_feature("free", "web_editor")
        assert TierFeatures.has_feature("free", "community_support")
        assert not TierFeatures.has_feature("free", "sso")
        assert not TierFeatures.has_feature("free", "webhooks")

    def test_professional_tier_features(self) -> None:
        """Test professional tier feature availability."""
        enforcer = SubscriptionEnforcer()

        # Professional gets more features
        assert TierFeatures.has_feature("professional", "webhooks")
        assert TierFeatures.has_feature("professional", "api_write")
        assert not TierFeatures.has_feature("professional", "sso")

    def test_enterprise_tier_features(self) -> None:
        """Test enterprise tier feature availability."""
        assert TierFeatures.has_feature("enterprise", "sso")
        assert TierFeatures.has_feature("enterprise", "saml")
        assert TierFeatures.has_feature("enterprise", "webhooks")

    def test_enforce_feature_access(self) -> None:
        """Test enforcing feature access by tier."""
        enforcer = SubscriptionEnforcer()

        # Free tier cannot access webhooks
        result = enforcer.check_feature_access("free", "webhooks")
        assert result["allowed"] is False
        assert result["required_tier"] == "professional"

        # Professional tier can access webhooks
        result = enforcer.check_feature_access("professional", "webhooks")
        assert result["allowed"] is True

    def test_get_tier_limits(self) -> None:
        """Test getting API limits by tier."""
        enforcer = SubscriptionEnforcer()

        free_limits = enforcer.get_tier_limits("free")
        prof_limits = enforcer.get_tier_limits("professional")

        assert free_limits["api_calls_per_month"] == 100
        assert prof_limits["api_calls_per_month"] == 10000
        assert prof_limits["storage_bytes"] > free_limits["storage_bytes"]

    def test_get_features_for_tier(self) -> None:
        """Test getting feature list for tier."""
        free_features = TierFeatures.get_features_for_tier("free")
        prof_features = TierFeatures.get_features_for_tier("professional")

        assert "web_editor" in free_features
        assert "webhooks" in prof_features
        assert "webhooks" not in free_features


# ============================================================================
# Test RevOps Metrics
# ============================================================================


class TestRevOpsMetrics:
    """Tests for revenue operations metrics."""

    def test_calculate_mrr(self) -> None:
        """Test Monthly Recurring Revenue calculation."""
        subscriptions = [
            {"status": "active", "monthly_cost": Decimal("49")},
            {"status": "active", "monthly_cost": Decimal("499")},
            {"status": "cancelled", "monthly_cost": Decimal("99")},  # Should be ignored
        ]

        mrr = calculate_mrr(subscriptions)
        assert mrr == Decimal("548")  # 49 + 499

    def test_get_mrr_from_database(self, db_session: Session) -> None:
        """Test retrieving MRR from database."""
        # Create multiple subscriptions
        user1 = User(username="user1", email="user1@example.com", password_hash=b"hash", api_key="key1")
        user2 = User(username="user2", email="user2@example.com", password_hash=b"hash", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.commit()

        sub1 = Subscription(
            user_id=user1.id,
            tier=SubscriptionTier.PROFESSIONAL,
            status="active",
            monthly_cost=Decimal("49"),
            start_date=datetime.now(UTC),
        )
        sub2 = Subscription(
            user_id=user2.id,
            tier=SubscriptionTier.ENTERPRISE,
            status="active",
            monthly_cost=Decimal("499"),
            start_date=datetime.now(UTC),
        )
        db_session.add_all([sub1, sub2])
        db_session.commit()

        mrr = get_mrr(db_session)
        assert mrr == Decimal("548")

    def test_get_revenue_by_tier(self, db_session: Session) -> None:
        """Test getting revenue breakdown by tier."""
        user1 = User(username="user1", email="user1@example.com", password_hash=b"hash", api_key="key1")
        user2 = User(username="user2", email="user2@example.com", password_hash=b"hash", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.commit()

        sub1 = Subscription(
            user_id=user1.id,
            tier=SubscriptionTier.PROFESSIONAL,
            status="active",
            monthly_cost=Decimal("49"),
            start_date=datetime.now(UTC),
        )
        sub2 = Subscription(
            user_id=user2.id,
            tier=SubscriptionTier.PROFESSIONAL,
            status="active",
            monthly_cost=Decimal("49"),
            start_date=datetime.now(UTC),
        )
        db_session.add_all([sub1, sub2])
        db_session.commit()

        revenue = get_revenue_by_tier(db_session)

        assert revenue["professional"]["count"] == 2
        assert float(revenue["professional"]["mrr"]) == 98.0


# ============================================================================
# Test End-to-End Workflows
# ============================================================================


class TestEndToEndWorkflows:
    """Tests for complete billing workflows."""

    def test_free_to_paid_conversion(self, db_session: Session, test_user_id: int) -> None:
        """Test free → professional conversion workflow."""
        # Step 1: User starts with free tier
        create_subscription(db_session, test_user_id, tier="free")
        sub = get_subscription(db_session, test_user_id)
        assert sub["tier"] == "free"

        # Step 2: User tracks some usage
        track_usage_event(db_session, test_user_id, "api_calls", 150)
        status = get_usage_quota_status(db_session, test_user_id)
        assert status["exceeded"] is True

        # Step 3: User upgrades to professional
        update_subscription_tier(db_session, test_user_id, "professional")
        sub = get_subscription(db_session, test_user_id)
        assert sub["tier"] == "professional"

        # Step 4: Now they have more quota
        status = get_usage_quota_status(db_session, test_user_id)
        assert status["api_quota"] == 10000
        assert status["exceeded"] is False

    def test_monthly_billing_cycle(self, db_session: Session, test_user_id: int) -> None:
        """Test complete monthly billing cycle."""
        # Step 1: Subscribe to professional
        create_subscription(db_session, test_user_id, tier="professional")

        # Step 2: Use API throughout month
        track_usage_event(db_session, test_user_id, "api_calls", 5000)
        track_usage_event(db_session, test_user_id, "api_calls", 3000)

        # Step 3: Generate invoice at month end
        invoice_result = generate_invoice(db_session, test_user_id)
        assert invoice_result["status"] == "draft"
        assert float(invoice_result["amount"]) == 49.0  # No overage

        # Step 4: Payment received (simulating webhook)
        mark_invoice_paid(db_session, invoice_result["invoice_id"])

        # Step 5: Verify invoice is paid
        invoices = get_invoices(db_session, test_user_id)
        assert invoices[0]["status"] == "paid"

    def test_overage_billing(self, db_session: Session, test_user_id: int) -> None:
        """Test billing with overage charges."""
        # Step 1: Free tier user
        create_subscription(db_session, test_user_id, tier="free")

        # Step 2: Heavy usage (exceeds quota by 500%)
        track_usage_event(db_session, test_user_id, "api_calls", 600)

        # Step 3: Invoice includes overage
        invoice_result = generate_invoice(db_session, test_user_id)
        amount = float(invoice_result["amount"])

        # Free tier = $0, 500 overage * $0.05 = $25.00
        assert amount == 25.0

        # Step 4: Invoice shows overage details
        line_items = invoice_result["line_items"]
        assert len(line_items) == 2  # Subscription (free) + overage
        assert any("Overage" in item["description"] for item in line_items)
