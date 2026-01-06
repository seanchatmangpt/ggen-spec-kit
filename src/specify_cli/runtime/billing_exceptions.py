"""
Billing domain exceptions - Andon pattern (fail-fast, fail-loud)
================================================================

These exceptions implement the Andon pattern from lean manufacturing:
- Fail immediately when quality issues detected
- Make errors visible and loud (no silent failures)
- Alert operations to investigate root cause
- Prevent broken state from propagating

Never silently degrade. Always raise and alert.
"""

from __future__ import annotations


class BillingException(Exception):
    """Base exception for all billing domain errors."""

    def __init__(self, message: str, error_code: str | None = None, context: dict | None = None):
        """Initialize billing exception.

        Parameters
        ----------
        message : str
            Human-readable error message.
        error_code : str, optional
            Machine-readable error code for monitoring/alerting.
        context : dict, optional
            Additional context about the error.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.error_code}): {self.message}"


class InvalidSubscriptionTier(BillingException):
    """Raised when invalid subscription tier requested (Andon: stop-the-line)."""

    pass


class SubscriptionNotFound(BillingException):
    """Raised when subscription doesn't exist (Andon: no silent null returns)."""

    pass


class SubscriptionNotActive(BillingException):
    """Raised when operation requires active subscription (Andon: enforce preconditions)."""

    pass


class InvalidBillingPeriod(BillingException):
    """Raised when billing period format is invalid (Andon: strict validation)."""

    pass


class InvoiceAlreadyExists(BillingException):
    """Raised when attempting to create duplicate invoice (Andon: prevent duplicates)."""

    pass


class UsageTrackingFailed(BillingException):
    """Raised when usage tracking fails (Andon: catch tracking issues early)."""

    pass


class InvalidFeatureTier(BillingException):
    """Raised when feature tier is invalid (Andon: enforce feature access)."""

    pass


class InvoiceNotFound(BillingException):
    """Raised when invoice doesn't exist (Andon: fail on missing resources)."""

    pass


class ConflictingOperation(BillingException):
    """Raised when operation conflicts with current state (Andon: enforce state machine)."""

    pass
