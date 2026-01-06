"""
tests/test_integration_e2e.py - End-to-End Integration Tests

Validates that all semantic, spec, MCP, and RevOps capabilities work together
in a complete, production-ready system.
"""

from __future__ import annotations

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from specify_cli.db.models import (
    Base,
    Subscription,
    UsageEvent,
    Invoice,
    SubscriptionTier,
    InvoiceStatus,
)
from specify_cli.ops.billing import (
    SubscriptionConfig,
    calculate_mrr,
    calculate_arr,
    aggregate_usage_by_period,
    apply_overage_charges,
)
from specify_cli.runtime.billing import (
    create_subscription,
    get_subscription,
    update_subscription_tier,
    cancel_subscription,
    track_usage_event,
    get_usage_for_period,
    get_usage_quota_status,
    generate_invoice,
    get_invoices,
    mark_invoice_paid,
    get_mrr,
    get_revenue_by_tier,
)
from specify_cli.security.subscription_enforcement import (
    TierFeatures,
    SubscriptionEnforcer,
)


@pytest.fixture
def db_session():
    """In-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestArchitectureIntegration:
    """Validate three-tier architecture."""

    def test_operations_layer_is_pure(self):
        """Verify ops layer has no SQLAlchemy imports."""
        from pathlib import Path

        ops_file = Path("src/specify_cli/ops/billing.py").read_text()

        # Operations should not import SQLAlchemy or runtime
        assert "from sqlalchemy" not in ops_file
        assert "from specify_cli.runtime" not in ops_file
        assert "session.add" not in ops_file
        assert "session.commit" not in ops_file

        # Verify specific operations exist and are callable
        assert callable(calculate_mrr)
        assert callable(apply_overage_charges)
        assert callable(aggregate_usage_by_period)

    def test_runtime_layer_uses_database(self):
        """Verify runtime layer uses SQLAlchemy."""
        from pathlib import Path

        runtime_file = Path("src/specify_cli/runtime/billing.py").read_text()

        # Runtime module should use SQLAlchemy
        assert "from sqlalchemy" in runtime_file
        assert "session.add" in runtime_file
        assert "session.commit" in runtime_file

    @pytest.mark.skipif(
        __import__("sys").modules.get("fastmcp") is None,
        reason="fastmcp not installed"
    )
    def test_mcp_layer_uses_runtime(self):
        """Verify MCP layer calls runtime functions."""
        from specify_cli.mcp.server import create_revops_server

        # MCP server should initialize without errors
        mcp = create_revops_server("sqlite:///:memory:")
        assert mcp is not None
        assert hasattr(mcp, "create_subscription")
        assert hasattr(mcp, "generate_invoice")


class TestRevOpsFullStack:
    """Test complete RevOps functionality."""

    def test_user_signup_to_invoice(self, db_session: Session):
        """Test complete user flow from signup to invoice."""
        # 1. User signs up with free tier
        user_id = 1000
        sub = create_subscription(db_session, user_id=user_id, tier="free")
        assert sub["tier"] == "free"
        assert sub["status"] == "active"

        # 2. User tracks API usage
        track_usage_event(db_session, user_id=user_id, metric_type="api_calls", amount=50)
        track_usage_event(db_session, user_id=user_id, metric_type="api_calls", amount=30)

        # 3. Check quota status
        status = get_usage_quota_status(db_session, user_id=user_id)
        assert status["api_calls_used"] == 80
        assert status["percentage_used"] == 80.0
        assert status["warning"] is True  # 80% = warning threshold

        # 4. User upgrades to professional
        upgraded = update_subscription_tier(db_session, user_id=user_id, new_tier="professional")
        assert upgraded["tier"] == "professional"
        assert upgraded["api_quota"] == 10000
        assert float(upgraded["monthly_cost"]) == 49.0

        # 5. Generate invoice
        invoice = generate_invoice(db_session, user_id=user_id)
        assert invoice["invoice_id"] is not None
        assert invoice["status"] == "draft"
        # Should have base cost (49) since we tracked 80 api calls before upgrade
        # and professional has 10k quota
        assert float(invoice["amount"]) >= 49.0

        # 6. Mark payment received
        marked = mark_invoice_paid(db_session, invoice["invoice_id"])
        assert marked["status"] == "paid"

    def test_multiple_users_revenue_metrics(self, db_session: Session):
        """Test revenue metrics across multiple users."""
        # Create multiple subscriptions
        sub1 = create_subscription(db_session, user_id=100, tier="free")
        sub2 = create_subscription(db_session, user_id=101, tier="professional")
        sub3 = create_subscription(db_session, user_id=102, tier="professional")
        sub4 = create_subscription(db_session, user_id=103, tier="enterprise")

        # Calculate MRR
        mrr = get_mrr(db_session)
        # 2 × $49 + 1 × $499 = $597
        assert float(mrr) == 597.0

        # Get revenue breakdown
        breakdown = get_revenue_by_tier(db_session)
        assert breakdown["free"]["count"] == 1
        assert breakdown["professional"]["count"] == 2
        assert breakdown["enterprise"]["count"] == 1

    def test_quota_enforcement_workflow(self, db_session: Session):
        """Test quota enforcement across different tiers."""
        # Test free tier: 100 API calls/month - test at quota and beyond
        free_sub = create_subscription(db_session, user_id=200, tier="free")
        track_usage_event(db_session, user_id=200, metric_type="api_calls", amount=100)
        free_status = get_usage_quota_status(db_session, user_id=200)
        assert free_status["exceeded"] is False  # 100 == 100 is not exceeded
        assert free_status["warning"] is True  # 100% usage triggers warning at >= 80%
        assert free_status["percentage_used"] == 100.0

        # Test beyond quota
        track_usage_event(db_session, user_id=200, metric_type="api_calls", amount=50)
        free_status = get_usage_quota_status(db_session, user_id=200)
        assert free_status["exceeded"] is True  # 150 > 100
        assert free_status["percentage_used"] == 150.0

        # Test professional tier: 10,000 API calls/month
        prof_sub = create_subscription(db_session, user_id=201, tier="professional")
        track_usage_event(db_session, user_id=201, metric_type="api_calls", amount=5000)
        prof_status = get_usage_quota_status(db_session, user_id=201)
        assert prof_status["exceeded"] is False
        assert prof_status["warning"] is False
        assert prof_status["percentage_used"] == 50.0

        # Test enterprise tier: 100,000 API calls/month
        ent_sub = create_subscription(db_session, user_id=202, tier="enterprise")
        track_usage_event(db_session, user_id=202, metric_type="api_calls", amount=50000)
        ent_status = get_usage_quota_status(db_session, user_id=202)
        # Enterprise quota is 100000, so 50000 is 50%
        assert ent_status["exceeded"] is False
        assert ent_status["percentage_used"] == 50.0

    def test_overage_billing_calculation(self, db_session: Session):
        """Test overage billing for usage beyond quota."""
        # Create professional subscription (10k quota)
        sub = create_subscription(db_session, user_id=300, tier="professional")

        # Track usage exceeding quota
        track_usage_event(db_session, user_id=300, metric_type="api_calls", amount=12000)

        # Generate invoice should include overage charges
        invoice = generate_invoice(db_session, user_id=300)

        # Base cost: $49
        # Overage: 2000 × $0.05 = $100
        # Total: $149
        expected_amount = 49.0 + 100.0
        assert float(invoice["amount"]) == expected_amount

        # Verify line items
        has_subscription = any(
            "Professional" in item.get("description", "")
            for item in invoice["line_items"]
        )
        has_overage = any(
            "Overage" in item.get("description", "")
            for item in invoice["line_items"]
        )
        assert has_subscription
        assert has_overage


class TestFeatureAccessControl:
    """Test feature gating by subscription tier."""

    def test_feature_matrix(self):
        """Test that feature matrix is correctly enforced."""
        enforcer = SubscriptionEnforcer()

        # Test each tier's feature set
        free_features = TierFeatures.get_features_for_tier("free")
        prof_features = TierFeatures.get_features_for_tier("professional")
        ent_features = TierFeatures.get_features_for_tier("enterprise")

        # Verify feature hierarchy
        assert len(free_features) < len(prof_features) < len(ent_features)

        # Test specific features
        assert "api_read" in free_features
        assert "webhooks" not in free_features
        assert "webhooks" in prof_features
        assert "sso" not in prof_features
        assert "sso" in ent_features

    def test_tier_limits(self):
        """Test that rate limits are correctly configured."""
        enforcer = SubscriptionEnforcer()

        free_limits = enforcer.get_tier_limits("free")
        prof_limits = enforcer.get_tier_limits("professional")
        ent_limits = enforcer.get_tier_limits("enterprise")

        # Verify limit hierarchy
        assert free_limits["api_calls_per_month"] < prof_limits["api_calls_per_month"]
        assert prof_limits["api_calls_per_month"] < ent_limits["api_calls_per_month"]

        # Verify specific values
        assert free_limits["api_calls_per_month"] == 100
        assert prof_limits["api_calls_per_month"] == 10000
        assert ent_limits["api_calls_per_month"] == 100000

    def test_feature_access_check(self):
        """Test feature access control logic."""
        enforcer = SubscriptionEnforcer()

        # Feature available in tier
        result = enforcer.check_feature_access("professional", "webhooks")
        assert result["allowed"] is True

        # Feature not available in tier
        result = enforcer.check_feature_access("free", "webhooks")
        assert result["allowed"] is False
        assert "required_tier" in result


class TestOperationsLayerPurity:
    """Verify operations layer is pure and reusable."""

    def test_usage_aggregation_pure(self):
        """Test usage aggregation as pure function."""
        events = [
            {"metric_type": "api_calls", "amount": 100, "billing_period": "2026-01"},
            {"metric_type": "api_calls", "amount": 50, "billing_period": "2026-01"},
            {"metric_type": "storage", "amount": 1000, "billing_period": "2026-01"},
        ]

        result1 = aggregate_usage_by_period(events, "2026-01")
        result2 = aggregate_usage_by_period(events, "2026-01")

        assert result1 == result2
        assert result1["api_calls"] == 150
        assert result1["storage"] == 1000

    def test_overage_calculation_pure(self):
        """Test overage calculation as pure function."""
        # apply_overage_charges takes overage_amount and multiplies by rate
        # Usage: 12000, Quota: 10000, so overage_amount = 2000
        # With rate $0.05/unit, charge = 2000 * 0.05 = 100
        from decimal import Decimal

        overage_amount = 2000
        overage1 = apply_overage_charges(overage_amount)
        overage2 = apply_overage_charges(overage_amount)

        assert overage1 == overage2
        # 2000 * 0.05 = 100.0
        assert float(overage1) == 100.0

        # Test custom rate
        overage3 = apply_overage_charges(2000, Decimal("0.10"))
        assert float(overage3) == 200.0


class TestTypeSafety:
    """Verify type hints and safety."""

    def test_function_type_hints(self):
        """Verify critical functions have type hints."""
        import inspect

        # Check operations layer
        sig = inspect.signature(calculate_mrr)
        assert sig.parameters["active_subscriptions"].annotation != inspect.Parameter.empty
        assert sig.return_annotation != inspect.Signature.empty

        # Check runtime layer
        sig = inspect.signature(create_subscription)
        assert sig.parameters["user_id"].annotation != inspect.Parameter.empty
        assert sig.parameters["tier"].annotation != inspect.Parameter.empty

    def test_model_type_definitions(self):
        """Verify database models have proper types."""
        # Verify Subscription model
        assert hasattr(Subscription, "user_id")
        assert hasattr(Subscription, "tier")
        assert hasattr(Subscription, "monthly_cost")

        # Verify UsageEvent model
        assert hasattr(UsageEvent, "metric_type")
        assert hasattr(UsageEvent, "amount")
        assert hasattr(UsageEvent, "billing_period")


class TestMCPIntegration:
    """Test MCP server integration."""

    @pytest.mark.skipif(
        __import__("sys").modules.get("fastmcp") is None,
        reason="fastmcp not installed"
    )
    def test_mcp_server_creation(self):
        """Test MCP server can be created."""
        from specify_cli.mcp.server import create_revops_server

        mcp = create_revops_server("sqlite:///:memory:")
        assert mcp is not None

    @pytest.mark.skipif(
        __import__("sys").modules.get("fastmcp") is None,
        reason="fastmcp not installed"
    )
    def test_mcp_tools_available(self):
        """Test all required MCP tools are available."""
        from specify_cli.mcp.server import create_revops_server

        mcp = create_revops_server("sqlite:///:memory:")

        required_tools = [
            "create_subscription",
            "get_subscription",
            "upgrade_subscription",
            "cancel_subscription",
            "track_usage",
            "get_usage_status",
            "get_usage_history",
            "generate_invoice",
            "get_invoices",
            "mark_payment_received",
            "get_monthly_recurring_revenue",
            "get_annual_recurring_revenue",
            "get_revenue_breakdown",
            "check_feature_access",
            "get_tier_features",
            "get_tier_limits",
            "get_subscription_tiers",
            "get_revops_status",
        ]

        for tool in required_tools:
            assert hasattr(mcp, tool), f"Missing MCP tool: {tool}"


class TestSystemStability:
    """Test system stability under load."""

    def test_multiple_subscriptions(self, db_session: Session):
        """Test creating many subscriptions."""
        for i in range(100):
            create_subscription(db_session, user_id=i, tier="professional")

        # Verify all created
        count = db_session.query(func.count(Subscription.id)).scalar()
        assert count == 100

    def test_usage_event_volume(self, db_session: Session):
        """Test tracking many usage events."""
        user_id = 500

        create_subscription(db_session, user_id=user_id, tier="professional")

        for i in range(1000):
            track_usage_event(
                db_session,
                user_id=user_id,
                metric_type="api_calls",
                amount=1.0,
            )

        # Verify aggregation works at scale
        usage = get_usage_for_period(db_session, user_id=user_id)
        assert usage["api_calls"] == 1000.0

    def test_invoice_generation_consistency(self, db_session: Session):
        """Test invoice generation is consistent and prevents duplicates."""
        user_id = 600

        create_subscription(db_session, user_id=user_id, tier="professional")
        track_usage_event(
            db_session, user_id=user_id, metric_type="api_calls", amount=5000
        )

        # Generate invoice first time
        inv1 = generate_invoice(db_session, user_id=user_id)
        assert inv1["invoice_id"] is not None
        assert inv1["status"] == "draft"
        assert "amount" in inv1

        # Try to generate same invoice again - should return error
        inv2 = generate_invoice(db_session, user_id=user_id)
        assert "error" in inv2  # Duplicate prevention
        assert inv2.get("error") == "Invoice already exists for this period"

        # Generate for different billing period should work
        inv3 = generate_invoice(db_session, user_id=user_id, billing_period="2025-12")
        assert inv3["invoice_id"] is not None
        assert inv3["invoice_id"] != inv1["invoice_id"]
