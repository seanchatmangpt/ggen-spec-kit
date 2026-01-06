"""
specify_cli.mcp.__main__ - MCP Server Entry Point

Starts the RevOps MCP server for integration with Claude and other MCP clients.

Usage:
    python -m specify_cli.mcp.server
    python -m specify_cli.mcp.server --db postgresql://user:pass@localhost/revops
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from .server import create_revops_server


async def main() -> None:
    """Start the RevOps MCP server."""
    # Default to SQLite for local development
    db_url = "sqlite:///./revops.db"

    # Allow override via environment variable
    import os

    if "DATABASE_URL" in os.environ:
        db_url = os.environ["DATABASE_URL"]

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--db" and len(sys.argv) > 2:
            db_url = sys.argv[2]
        elif sys.argv[1].startswith("--db="):
            db_url = sys.argv[1].split("=", 1)[1]

    print(f"Starting RevOps MCP Server")
    print(f"Database: {db_url}")
    print()

    try:
        server = create_revops_server(db_url)
        print("✓ RevOps MCP Server initialized")
        print()
        print("Available Tools:")
        print("  Subscriptions:")
        print("    - create_subscription")
        print("    - get_subscription")
        print("    - upgrade_subscription")
        print("    - cancel_subscription")
        print()
        print("  Usage & Quotas:")
        print("    - track_usage")
        print("    - get_usage_status")
        print("    - get_usage_history")
        print()
        print("  Invoicing:")
        print("    - generate_invoice")
        print("    - get_invoices")
        print("    - mark_payment_received")
        print()
        print("  Revenue Metrics:")
        print("    - get_monthly_recurring_revenue")
        print("    - get_annual_recurring_revenue")
        print("    - get_revenue_breakdown")
        print()
        print("  Feature Access:")
        print("    - check_feature_access")
        print("    - get_tier_features")
        print("    - get_tier_limits")
        print()
        print("  Configuration:")
        print("    - get_subscription_tiers")
        print("    - get_revops_status")
        print()
        print("Ready to accept MCP client connections")
        print("Press Ctrl+C to stop")
        print()

        # Keep server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down RevOps MCP Server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
