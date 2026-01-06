"""
specify_cli.commands.billing - Revenue Operations CLI Commands
==============================================================

CLI interface for subscription management, usage tracking, invoicing, and
revenue metrics. Exposes all RevOps capabilities from the command line.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.instrumentation import add_span_event, instrument_command
from specify_cli.core.shell import colour
from specify_cli.runtime.billing import (
    create_subscription,
    get_subscription,
    update_subscription_tier,
    cancel_subscription,
    track_usage_event,
    get_usage_quota_status,
    get_usage_for_period,
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
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from specify_cli.db.models import Base

app = typer.Typer(help="Revenue Operations and Billing Management")
console = Console()

# Default to SQLite for CLI usage
DEFAULT_DB = "sqlite:///./revops.db"


def _get_session():
    """Get database session for CLI commands."""
    engine = create_engine(DEFAULT_DB)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


# ============================================================================
# Subscription Commands
# ============================================================================


@app.command("create-subscription")
@instrument_command("billing.create_subscription", track_args=True)
def create_sub_command(
    user_id: int = typer.Argument(..., help="User ID"),
    tier: str = typer.Option("free", "--tier", help="Subscription tier: free, professional, enterprise"),
) -> None:
    """Create a new subscription for a user."""
    try:
        add_span_event("billing.create_subscription.started", {"user_id": user_id, "tier": tier})

        session = _get_session()
        try:
            result = create_subscription(session, user_id, tier)

            if "error" in result:
                colour(f"[red]✗ Error:[/red] {result['error']}", "red")
                raise typer.Exit(1)

            console.print(f"[bold green]✓[/] Subscription created for user {user_id}")
            console.print(f"  Tier: {result.get('tier')}")
            console.print(f"  Status: {result.get('status')}")
            console.print(f"  Cost: ${result.get('monthly_cost')}/month")
            console.print(f"  API Quota: {result.get('api_quota')} calls/month")

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("get-subscription")
@instrument_command("billing.get_subscription", track_args=True)
def get_sub_command(
    user_id: int = typer.Argument(..., help="User ID"),
) -> None:
    """Get subscription details for a user."""
    try:
        add_span_event("billing.get_subscription.started", {"user_id": user_id})

        session = _get_session()
        try:
            result = get_subscription(session, user_id)

            if result is None or "error" in result:
                colour(f"[red]✗ No active subscription found for user {user_id}[/red]", "red")
                raise typer.Exit(1)

            console.print(f"[bold]Subscription for User {user_id}[/bold]")
            table = Table(show_header=False)
            table.add_row("Tier", result.get("tier"))
            table.add_row("Status", result.get("status"))
            table.add_row("Monthly Cost", f"${result.get('monthly_cost')}")
            table.add_row("API Quota", f"{result.get('api_quota')} calls")
            table.add_row("Storage Quota", f"{result.get('storage_quota')} bytes")
            table.add_row("Started", str(result.get("start_date")))
            console.print(table)

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("upgrade-subscription")
@instrument_command("billing.update_subscription_tier", track_args=True)
def upgrade_sub_command(
    user_id: int = typer.Argument(..., help="User ID"),
    tier: str = typer.Option(..., "--tier", help="New tier: free, professional, enterprise"),
) -> None:
    """Upgrade or downgrade subscription tier."""
    try:
        add_span_event("billing.update_subscription_tier.started", {"user_id": user_id, "tier": tier})

        session = _get_session()
        try:
            result = update_subscription_tier(session, user_id, tier)

            if "error" in result:
                colour(f"[red]✗ Error:[/red] {result['error']}", "red")
                raise typer.Exit(1)

            console.print(f"[bold green]✓[/] Upgraded user {user_id} to {tier} tier")
            console.print(f"  New Cost: ${result.get('monthly_cost')}/month")
            console.print(f"  New API Quota: {result.get('api_quota')} calls/month")

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("cancel-subscription")
@instrument_command("billing.cancel_subscription", track_args=True)
def cancel_sub_command(
    user_id: int = typer.Argument(..., help="User ID"),
) -> None:
    """Cancel a subscription."""
    try:
        add_span_event("billing.cancel_subscription.started", {"user_id": user_id})

        session = _get_session()
        try:
            result = cancel_subscription(session, user_id)

            if "error" in result:
                colour(f"[red]✗ Error:[/red] {result['error']}", "red")
                raise typer.Exit(1)

            console.print(f"[bold green]✓[/] Subscription cancelled for user {user_id}")
            console.print(f"  Ended: {result.get('cancelled_date')}")

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


# ============================================================================
# Usage Tracking & Quota Commands
# ============================================================================


@app.command("track-usage")
@instrument_command("billing.track_usage_event", track_args=True)
def track_usage_command(
    user_id: int = typer.Argument(..., help="User ID"),
    metric_type: str = typer.Option(..., "--metric", help="Metric type: api_calls, storage, webhooks"),
    amount: float = typer.Option(..., "--amount", help="Amount consumed"),
) -> None:
    """Track usage event for a user."""
    try:
        add_span_event("billing.track_usage_event.started", {
            "user_id": user_id,
            "metric_type": metric_type,
            "amount": amount
        })

        session = _get_session()
        try:
            result = track_usage_event(session, user_id, metric_type, amount)

            if "error" in result:
                colour(f"[red]✗ Error:[/red] {result['error']}", "red")
                raise typer.Exit(1)

            console.print(f"[bold green]✓[/] Usage tracked for user {user_id}")
            console.print(f"  Metric: {metric_type}")
            console.print(f"  Amount: {amount}")
            console.print(f"  Timestamp: {result.get('timestamp')}")

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("get-usage")
@instrument_command("billing.get_usage_quota_status", track_args=True)
def get_usage_command(
    user_id: int = typer.Argument(..., help="User ID"),
) -> None:
    """Get current usage and quota status for a user."""
    try:
        add_span_event("billing.get_usage_quota_status.started", {"user_id": user_id})

        session = _get_session()
        try:
            result = get_usage_quota_status(session, user_id)

            if "error" in result:
                colour(f"[red]✗ Error:[/red] {result['error']}", "red")
                raise typer.Exit(1)

            console.print(f"[bold]Usage Status for User {user_id}[/bold]")
            table = Table(show_header=False)
            table.add_row("Tier", result.get("tier"))
            table.add_row("API Quota", f"{result.get('api_quota')} calls")
            table.add_row("API Used", f"{result.get('api_calls_used')} calls")
            table.add_row("Remaining", f"{result.get('remaining')} calls")
            table.add_row("Percentage Used", f"{result.get('percentage_used'):.1f}%")

            status_color = "red" if result.get("exceeded") else "yellow" if result.get("warning") else "green"
            status_text = "EXCEEDED" if result.get("exceeded") else "WARNING" if result.get("warning") else "OK"
            table.add_row("Status", f"[{status_color}]{status_text}[/{status_color}]")

            console.print(table)

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


# ============================================================================
# Invoicing & Payments Commands
# ============================================================================


@app.command("generate-invoice")
@instrument_command("billing.generate_invoice", track_args=True)
def gen_invoice_command(
    user_id: int = typer.Argument(..., help="User ID"),
    billing_period: Optional[str] = typer.Option(None, "--period", help="Billing period (YYYY-MM)"),
) -> None:
    """Generate invoice for a user."""
    try:
        add_span_event("billing.generate_invoice.started", {"user_id": user_id})

        session = _get_session()
        try:
            result = generate_invoice(session, user_id, billing_period)

            if "error" in result:
                colour(f"[yellow]⚠ {result['error']}[/yellow]", "yellow")
                return

            console.print(f"[bold green]✓[/] Invoice generated for user {user_id}")
            table = Table(show_header=False)
            table.add_row("Invoice ID", result.get("invoice_id"))
            table.add_row("Amount", f"${result.get('amount')}")
            table.add_row("Status", result.get("status"))
            table.add_row("Issue Date", str(result.get("issue_date")))
            table.add_row("Due Date", str(result.get("due_date")))

            console.print(table)

            if result.get("line_items"):
                console.print("\n[bold]Line Items:[/bold]")
                items_table = Table(show_header=True)
                items_table.add_column("Description")
                items_table.add_column("Amount")
                for item in result.get("line_items", []):
                    items_table.add_row(item.get("description"), f"${item.get('amount')}")
                console.print(items_table)

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("mark-paid")
@instrument_command("billing.mark_invoice_paid", track_args=True)
def mark_paid_command(
    invoice_id: str = typer.Argument(..., help="Invoice ID"),
) -> None:
    """Mark invoice as paid."""
    try:
        add_span_event("billing.mark_invoice_paid.started", {"invoice_id": invoice_id})

        session = _get_session()
        try:
            result = mark_invoice_paid(session, invoice_id)

            if "error" in result:
                colour(f"[red]✗ Error:[/red] {result['error']}", "red")
                raise typer.Exit(1)

            console.print(f"[bold green]✓[/] Invoice {invoice_id} marked as paid")
            console.print(f"  Paid Date: {result.get('paid_date')}")

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


# ============================================================================
# Revenue Metrics Commands
# ============================================================================


@app.command("get-mrr")
@instrument_command("billing.get_mrr", track_args=True)
def get_mrr_command() -> None:
    """Get Monthly Recurring Revenue (MRR)."""
    try:
        add_span_event("billing.get_mrr.started", {})

        session = _get_session()
        try:
            mrr = get_mrr(session)

            console.print(f"[bold]Monthly Recurring Revenue (MRR)[/bold]")
            console.print(f"  [bold green]${float(mrr):,.2f}[/bold green]")
            console.print(f"\n  Annual Recurring Revenue (ARR): ${float(mrr) * 12:,.2f}")

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("get-revenue")
@instrument_command("billing.get_revenue_by_tier", track_args=True)
def get_revenue_command() -> None:
    """Get revenue breakdown by subscription tier."""
    try:
        add_span_event("billing.get_revenue_by_tier.started", {})

        session = _get_session()
        try:
            breakdown = get_revenue_by_tier(session)

            console.print(f"[bold]Revenue Breakdown by Tier[/bold]")
            table = Table(show_header=True)
            table.add_column("Tier")
            table.add_column("Subscribers")
            table.add_column("MRR")

            for tier, data in breakdown.items():
                if tier != "total":
                    table.add_row(
                        tier.capitalize(),
                        str(data.get("count", 0)),
                        f"${float(data.get('mrr', 0)):,.2f}"
                    )

            console.print(table)
            console.print(f"\n[bold]Total MRR:[/bold] ${float(breakdown.get('total', 0)):,.2f}")

        finally:
            session.close()

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


# ============================================================================
# Feature Access Commands
# ============================================================================


@app.command("check-feature")
@instrument_command("billing.check_feature_access", track_args=True)
def check_feature_command(
    tier: str = typer.Argument(..., help="Subscription tier: free, professional, enterprise"),
    feature: str = typer.Argument(..., help="Feature name to check"),
) -> None:
    """Check if a tier has access to a feature."""
    try:
        add_span_event("billing.check_feature_access.started", {"tier": tier, "feature": feature})

        enforcer = SubscriptionEnforcer()
        result = enforcer.check_feature_access(tier, feature)

        if result.get("allowed"):
            console.print(f"[bold green]✓[/] Feature '{feature}' is available in {tier} tier")
        else:
            console.print(f"[bold red]✗[/] Feature '{feature}' is NOT available in {tier} tier")
            console.print(f"  Required tier: {result.get('required_tier')}")
            console.print(f"  Reason: {result.get('reason')}")

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e


@app.command("get-features")
@instrument_command("billing.get_tier_features", track_args=True)
def get_features_command(
    tier: str = typer.Argument(..., help="Subscription tier: free, professional, enterprise"),
) -> None:
    """Get all features available in a tier."""
    try:
        add_span_event("billing.get_tier_features.started", {"tier": tier})

        features = TierFeatures.get_features_for_tier(tier)

        console.print(f"[bold]Features in {tier.capitalize()} Tier[/bold]")
        console.print(f"Total: {len(features)} features\n")

        for feature in features:
            console.print(f"  • {feature}")

    except Exception as e:
        colour(f"[red]Error:[/red] {e}", "red")
        raise typer.Exit(1) from e
