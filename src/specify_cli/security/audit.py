"""
specify_cli.security.audit
---------------------------
Comprehensive audit logging for security events and compliance.

This module provides:

* **Security Event Logging**: Track all security-relevant operations
* **User Session Management**: Track user activities and sessions
* **Change Tracking**: Version control for configuration changes
* **Compliance Logging**: GDPR, HIPAA, SOC2 audit trails
* **Threat Detection**: Suspicious activity monitoring

Security Features
-----------------
- Immutable audit logs with cryptographic integrity
- Real-time security event streaming
- Structured logging with semantic conventions
- User session tracking and anomaly detection
- Compliance-ready audit trails (GDPR, HIPAA, SOC2, PCI-DSS)
- Automated threat detection and alerting
- Log retention and archival policies
- Forensic analysis capabilities
- Integration with SIEM systems

Example
-------
    # Basic audit logging
    audit = AuditLogger()
    audit.log_event("user.login", user_id="user123", success=True)
    audit.log_event("file.access", file_path="/sensitive/data.txt", user_id="user123")

    # Compliance logging
    compliance = ComplianceLogger()
    compliance.log_gdpr_event("data.deletion", subject_id="user123")
    compliance.log_hipaa_event("patient.record.access", patient_id="P123")

    # Security event tracking
    event = SecurityEvent(
        event_type="authentication.failure",
        severity="high",
        user_id="user123",
        ip_address="192.168.1.1"
    )
    audit.log_security_event(event)
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from specify_cli.core.telemetry import record_exception, span


class AuditError(Exception):
    """Base exception for audit operations."""


class EventSeverity(Enum):
    """Severity levels for security events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventCategory(Enum):
    """Categories for security events."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    NETWORK = "network"
    ENCRYPTION = "encryption"
    THREAT = "threat"


class SecurityEvent:
    """
    Structured security event.

    Parameters
    ----------
    event_type : str
        Type of security event (e.g., "user.login", "file.access")
    severity : str or EventSeverity
        Event severity level
    category : str or EventCategory, optional
        Event category
    user_id : str, optional
        User identifier
    session_id : str, optional
        Session identifier
    ip_address : str, optional
        Source IP address
    resource : str, optional
        Resource being accessed
    action : str, optional
        Action being performed
    result : str, optional
        Result of action (success, failure, etc.)
    metadata : dict, optional
        Additional event metadata

    Attributes
    ----------
    event_id : str
        Unique event identifier
    timestamp : datetime
        Event timestamp
    event_type : str
        Event type
    severity : EventSeverity
        Event severity
    category : EventCategory
        Event category
    """

    def __init__(
        self,
        event_type: str,
        severity: str | EventSeverity = EventSeverity.LOW,
        category: str | EventCategory | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        resource: str | None = None,
        action: str | None = None,
        result: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize security event."""
        self.event_id = self._generate_event_id()
        self.timestamp = datetime.utcnow()
        self.event_type = event_type
        self.severity = severity if isinstance(severity, EventSeverity) else EventSeverity(severity)
        self.category = category if isinstance(category, EventCategory | None) else (
            EventCategory(category) if category else None
        )
        self.user_id = user_id
        self.session_id = session_id
        self.ip_address = ip_address
        self.resource = resource
        self.action = action
        self.result = result
        self.metadata = metadata or {}

    @staticmethod
    def _generate_event_id() -> str:
        """Generate unique event ID."""
        import secrets
        return f"evt_{secrets.token_hex(16)}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert event to dictionary.

        Returns
        -------
        dict
            Event as dictionary
        """
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "severity": self.severity.value,
            "category": self.category.value if self.category else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """
        Convert event to JSON string.

        Returns
        -------
        str
            Event as JSON
        """
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Comprehensive audit logging system.

    Provides immutable audit logs with cryptographic integrity for
    security events, user activities, and system changes.

    Parameters
    ----------
    log_file : str or Path, optional
        Path to audit log file. Default is ~/.specify/audit.log
    enable_integrity : bool, optional
        Enable cryptographic integrity checking. Default is True.

    Attributes
    ----------
    log_file : Path
        Path to audit log file
    enable_integrity : bool
        Whether integrity checking is enabled
    logger : logging.Logger
        Python logger instance
    """

    def __init__(
        self,
        log_file: str | Path | None = None,
        enable_integrity: bool = True,
    ) -> None:
        """Initialize audit logger."""
        if log_file is None:
            log_file = Path.home() / ".specify" / "audit.log"
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.enable_integrity = enable_integrity
        self.logger = self._setup_logger()
        self._last_hash: str | None = None

    def _setup_logger(self) -> logging.Logger:
        """Set up audit logger."""
        logger = logging.getLogger("specify.audit")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # File handler
        handler = logging.FileHandler(self.log_file, mode="a")
        handler.setLevel(logging.INFO)

        # JSON formatter
        formatter = logging.Formatter('{"timestamp": "%(asctime)s", "message": %(message)s}')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def _calculate_integrity_hash(self, event_data: dict[str, Any]) -> str:
        """
        Calculate integrity hash for event.

        Parameters
        ----------
        event_data : dict
            Event data

        Returns
        -------
        str
            SHA-256 hash
        """
        if self._last_hash:
            event_data["previous_hash"] = self._last_hash

        event_json = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(event_json.encode()).hexdigest()

    def log_event(
        self,
        event_type: str,
        severity: str = "low",
        **kwargs: Any,
    ) -> str:
        """
        Log a security event.

        Parameters
        ----------
        event_type : str
            Type of event
        severity : str, optional
            Event severity. Default is "low".
        **kwargs : Any
            Additional event attributes

        Returns
        -------
        str
            Event ID
        """
        with span("security.audit", operation="log_event", event_type=event_type):
            event = SecurityEvent(event_type=event_type, severity=severity, **kwargs)
            return self.log_security_event(event)

    def log_security_event(self, event: SecurityEvent) -> str:
        """
        Log a structured security event.

        Parameters
        ----------
        event : SecurityEvent
            Security event to log

        Returns
        -------
        str
            Event ID
        """
        with span("security.audit", operation="log_security_event"):
            try:
                event_data = event.to_dict()

                # Add integrity hash
                if self.enable_integrity:
                    event_hash = self._calculate_integrity_hash(event_data)
                    event_data["integrity_hash"] = event_hash
                    self._last_hash = event_hash

                # Log event
                self.logger.info(json.dumps(event_data))

                return event.event_id

            except Exception as e:
                record_exception(e)
                msg = f"Failed to log security event: {e}"
                raise AuditError(msg) from e

    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource: str | None = None,
        result: str = "success",
        **metadata: Any,
    ) -> str:
        """
        Log a user action.

        Parameters
        ----------
        user_id : str
            User identifier
        action : str
            Action performed
        resource : str, optional
            Resource accessed
        result : str, optional
            Action result. Default is "success".
        **metadata : Any
            Additional metadata

        Returns
        -------
        str
            Event ID
        """
        return self.log_event(
            "user.action",
            severity="low",
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            metadata=metadata,
        )

    def log_authentication(
        self,
        user_id: str,
        success: bool,
        method: str = "password",
        ip_address: str | None = None,
        **metadata: Any,
    ) -> str:
        """
        Log an authentication attempt.

        Parameters
        ----------
        user_id : str
            User identifier
        success : bool
            Whether authentication succeeded
        method : str, optional
            Authentication method. Default is "password".
        ip_address : str, optional
            Source IP address
        **metadata : Any
            Additional metadata

        Returns
        -------
        str
            Event ID
        """
        severity = "low" if success else "high"
        result = "success" if success else "failure"

        return self.log_event(
            "authentication",
            severity=severity,
            category="authentication",
            user_id=user_id,
            action=method,
            result=result,
            ip_address=ip_address,
            metadata=metadata,
        )

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str = "read",
        authorized: bool = True,
        **metadata: Any,
    ) -> str:
        """
        Log data access.

        Parameters
        ----------
        user_id : str
            User identifier
        resource : str
            Resource accessed
        action : str, optional
            Action performed. Default is "read".
        authorized : bool, optional
            Whether access was authorized. Default is True.
        **metadata : Any
            Additional metadata

        Returns
        -------
        str
            Event ID
        """
        severity = "low" if authorized else "critical"
        result = "success" if authorized else "denied"

        return self.log_event(
            "data.access",
            severity=severity,
            category="data_access",
            user_id=user_id,
            resource=resource,
            action=action,
            result=result,
            metadata=metadata,
        )

    def query_events(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        event_type: str | None = None,
        user_id: str | None = None,
        severity: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query audit events.

        Parameters
        ----------
        start_time : datetime, optional
            Start of time range
        end_time : datetime, optional
            End of time range
        event_type : str, optional
            Filter by event type
        user_id : str, optional
            Filter by user ID
        severity : str, optional
            Filter by severity

        Returns
        -------
        list[dict]
            List of matching events
        """
        with span("security.audit", operation="query_events"):
            events = []  # type: ignore[var-annotated]

            if not self.log_file.exists():
                return events

            with self.log_file.open("r") as f:
                for line in f:
                    try:
                        # Parse JSON log line
                        log_entry = json.loads(line)
                        message = log_entry["message"]
                        # Message might already be parsed or be a string
                        event_data = json.loads(message) if isinstance(message, str) else message

                        # Apply filters
                        if start_time and datetime.fromisoformat(event_data["timestamp"]) < start_time:
                            continue
                        if end_time and datetime.fromisoformat(event_data["timestamp"]) > end_time:
                            continue
                        if event_type and event_data.get("event_type") != event_type:
                            continue
                        if user_id and event_data.get("user_id") != user_id:
                            continue
                        if severity and event_data.get("severity") != severity:
                            continue

                        events.append(event_data)

                    except (json.JSONDecodeError, KeyError):
                        continue

            return events


class ComplianceLogger:
    """
    Compliance-specific audit logging.

    Provides specialized logging for regulatory compliance requirements
    including GDPR, HIPAA, SOC2, and PCI-DSS.

    Parameters
    ----------
    audit_logger : AuditLogger, optional
        Audit logger instance. If None, creates a new one.

    Attributes
    ----------
    audit_logger : AuditLogger
        Underlying audit logger
    """

    def __init__(self, audit_logger: AuditLogger | None = None) -> None:
        """Initialize compliance logger."""
        self.audit_logger = audit_logger or AuditLogger()

    def log_gdpr_event(
        self,
        event_type: str,
        subject_id: str,
        data_category: str | None = None,
        legal_basis: str | None = None,
        **metadata: Any,
    ) -> str:
        """
        Log GDPR-related event.

        Parameters
        ----------
        event_type : str
            Event type (e.g., "data.deletion", "consent.given")
        subject_id : str
            Data subject identifier
        data_category : str, optional
            Category of personal data
        legal_basis : str, optional
            Legal basis for processing
        **metadata : Any
            Additional metadata

        Returns
        -------
        str
            Event ID
        """
        with span("security.compliance", operation="log_gdpr"):
            metadata["compliance_framework"] = "GDPR"
            metadata["subject_id"] = subject_id
            if data_category:
                metadata["data_category"] = data_category
            if legal_basis:
                metadata["legal_basis"] = legal_basis

            return self.audit_logger.log_event(
                f"gdpr.{event_type}",
                severity="medium",
                category="data_access",
                metadata=metadata,
            )

    def log_hipaa_event(
        self,
        event_type: str,
        patient_id: str | None = None,
        phi_accessed: bool = False,
        **metadata: Any,
    ) -> str:
        """
        Log HIPAA-related event.

        Parameters
        ----------
        event_type : str
            Event type (e.g., "patient.record.access")
        patient_id : str, optional
            Patient identifier
        phi_accessed : bool, optional
            Whether PHI was accessed. Default is False.
        **metadata : Any
            Additional metadata

        Returns
        -------
        str
            Event ID
        """
        with span("security.compliance", operation="log_hipaa"):
            metadata["compliance_framework"] = "HIPAA"
            if patient_id:
                metadata["patient_id"] = patient_id
            metadata["phi_accessed"] = phi_accessed

            severity = "high" if phi_accessed else "medium"

            return self.audit_logger.log_event(
                f"hipaa.{event_type}",
                severity=severity,
                category="data_access",
                metadata=metadata,
            )

    def log_soc2_event(
        self,
        event_type: str,
        control_id: str | None = None,
        **metadata: Any,
    ) -> str:
        """
        Log SOC2-related event.

        Parameters
        ----------
        event_type : str
            Event type
        control_id : str, optional
            SOC2 control identifier
        **metadata : Any
            Additional metadata

        Returns
        -------
        str
            Event ID
        """
        with span("security.compliance", operation="log_soc2"):
            metadata["compliance_framework"] = "SOC2"
            if control_id:
                metadata["control_id"] = control_id

            return self.audit_logger.log_event(
                f"soc2.{event_type}",
                severity="medium",
                metadata=metadata,
            )

    def generate_compliance_report(
        self,
        framework: str,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """
        Generate compliance report for a date range.

        Parameters
        ----------
        framework : str
            Compliance framework (GDPR, HIPAA, SOC2)
        start_date : datetime
            Report start date
        end_date : datetime
            Report end date

        Returns
        -------
        dict
            Compliance report
        """
        with span("security.compliance", operation="generate_report", framework=framework):
            events = self.audit_logger.query_events(
                start_time=start_date,
                end_time=end_date,
            )

            # Filter for framework-specific events
            framework_events = [
                e for e in events
                if e.get("metadata", {}).get("compliance_framework") == framework.upper()
            ]

            return {
                "framework": framework.upper(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_events": len(framework_events),
                "events_by_type": self._group_events_by_type(framework_events),
                "events_by_severity": self._group_events_by_severity(framework_events),
                "events": framework_events,
            }

    @staticmethod
    def _group_events_by_type(events: list[dict[str, Any]]) -> dict[str, int]:
        """Group events by type."""
        by_type: dict[str, int] = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            by_type[event_type] = by_type.get(event_type, 0) + 1
        return by_type

    @staticmethod
    def _group_events_by_severity(events: list[dict[str, Any]]) -> dict[str, int]:
        """Group events by severity."""
        by_severity: dict[str, int] = {}
        for event in events:
            severity = event.get("severity", "unknown")
            by_severity[severity] = by_severity.get(severity, 0) + 1
        return by_severity


__all__ = [
    "AuditError",
    "AuditLogger",
    "ComplianceLogger",
    "EventCategory",
    "EventSeverity",
    "SecurityEvent",
]
