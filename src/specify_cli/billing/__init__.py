"""
specify_cli.billing - Billing & Revenue Operations Module
=========================================================

Revenue operations infrastructure for monetization models:
- Subscription management (SaaS licensing)
- Metered usage billing (Freemium API)
- Payment processing (Stripe integration)
- Invoice generation
- Support SLAs

This module implements the operations and payment layers for all revenue strategies
documented in REVENUE_STRATEGIES.md.
"""

from specify_cli.billing.stripe_integration import StripeClient, StripeConfig, StripeProducts

__all__ = [
    "StripeClient",
    "StripeConfig",
    "StripeProducts",
]
