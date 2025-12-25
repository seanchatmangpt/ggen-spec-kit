"""
Tests for security.audit module.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta

from specify_cli.security.audit import (
    AuditLogger,
    SecurityEvent,
    EventSeverity,
    EventCategory,
    ComplianceLogger,
)


@pytest.fixture
def audit_file(tmp_path: Path) -> Path:
    """Create temporary audit log file path."""
    return tmp_path / "audit.log"


@pytest.fixture
def audit_logger(audit_file: Path) -> AuditLogger:
    """Create audit logger instance."""
    return AuditLogger(log_file=audit_file)


class TestSecurityEvent:
    """Tests for SecurityEvent class."""

    def test_create_event_basic(self) -> None:
        """Test creating basic security event."""
        event = SecurityEvent("user.login", severity="high")

        assert event.event_type == "user.login"
        assert event.severity == EventSeverity.HIGH
        assert event.event_id.startswith("evt_")

    def test_event_to_dict(self) -> None:
        """Test converting event to dictionary."""
        event = SecurityEvent(
            "user.login",
            severity="high",
            user_id="user123",
            ip_address="192.168.1.1",
        )

        event_dict = event.to_dict()

        assert event_dict["event_type"] == "user.login"
        assert event_dict["severity"] == "high"
        assert event_dict["user_id"] == "user123"
        assert event_dict["ip_address"] == "192.168.1.1"

    def test_event_to_json(self) -> None:
        """Test converting event to JSON."""
        event = SecurityEvent("user.login", severity="low")
        event_json = event.to_json()

        # Should be valid JSON
        parsed = json.loads(event_json)
        assert parsed["event_type"] == "user.login"

    def test_event_with_metadata(self) -> None:
        """Test event with custom metadata."""
        metadata = {"browser": "Chrome", "device": "mobile"}
        event = SecurityEvent("user.login", metadata=metadata)

        event_dict = event.to_dict()
        assert event_dict["metadata"] == metadata


class TestAuditLogger:
    """Tests for AuditLogger class."""

    def test_log_event_basic(self, audit_logger: AuditLogger) -> None:
        """Test logging basic event."""
        event_id = audit_logger.log_event("user.login", severity="low", user_id="user123")

        assert event_id.startswith("evt_")

    def test_log_security_event(self, audit_logger: AuditLogger) -> None:
        """Test logging structured security event."""
        event = SecurityEvent(
            "authentication",
            severity="high",
            user_id="user123",
            result="failure",
        )

        event_id = audit_logger.log_security_event(event)
        assert event_id == event.event_id

    def test_log_user_action(self, audit_logger: AuditLogger) -> None:
        """Test logging user action."""
        event_id = audit_logger.log_user_action(
            user_id="user123",
            action="create",
            resource="/api/users",
            result="success",
        )

        assert event_id.startswith("evt_")

    def test_log_authentication(self, audit_logger: AuditLogger) -> None:
        """Test logging authentication event."""
        event_id = audit_logger.log_authentication(
            user_id="user123",
            success=True,
            method="password",
            ip_address="192.168.1.1",
        )

        assert event_id.startswith("evt_")

    def test_log_data_access(self, audit_logger: AuditLogger) -> None:
        """Test logging data access."""
        event_id = audit_logger.log_data_access(
            user_id="user123",
            resource="/sensitive/data.txt",
            action="read",
            authorized=True,
        )

        assert event_id.startswith("evt_")

    def test_query_events_all(self, audit_logger: AuditLogger, audit_file: Path) -> None:
        """Test querying all events."""
        # Log some events
        audit_logger.log_event("event1", severity="low")
        audit_logger.log_event("event2", severity="high")

        events = audit_logger.query_events()
        assert len(events) >= 2

    def test_query_events_by_type(self, audit_logger: AuditLogger) -> None:
        """Test querying events by type."""
        audit_logger.log_event("user.login", severity="low")
        audit_logger.log_event("user.logout", severity="low")
        audit_logger.log_event("data.access", severity="medium")

        events = audit_logger.query_events(event_type="user.login")
        assert all(e["event_type"] == "user.login" for e in events)

    def test_query_events_by_user(self, audit_logger: AuditLogger) -> None:
        """Test querying events by user."""
        audit_logger.log_event("event1", user_id="user123")
        audit_logger.log_event("event2", user_id="user456")

        events = audit_logger.query_events(user_id="user123")
        assert all(e["user_id"] == "user123" for e in events)

    def test_query_events_by_severity(self, audit_logger: AuditLogger) -> None:
        """Test querying events by severity."""
        audit_logger.log_event("event1", severity="low")
        audit_logger.log_event("event2", severity="high")

        events = audit_logger.query_events(severity="high")
        assert all(e["severity"] == "high" for e in events)

    def test_integrity_hash(self, audit_logger: AuditLogger) -> None:
        """Test integrity hash generation."""
        # Log two events
        audit_logger.log_event("event1")
        audit_logger.log_event("event2")

        # Verify audit log has integrity hashes
        events = audit_logger.query_events()
        assert all("integrity_hash" in e for e in events)


class TestComplianceLogger:
    """Tests for ComplianceLogger class."""

    def test_log_gdpr_event(self, audit_logger: AuditLogger) -> None:
        """Test logging GDPR event."""
        compliance = ComplianceLogger(audit_logger)

        event_id = compliance.log_gdpr_event(
            "data.deletion",
            subject_id="user123",
            data_category="personal",
            legal_basis="consent",
        )

        assert event_id.startswith("evt_")

    def test_log_hipaa_event(self, audit_logger: AuditLogger) -> None:
        """Test logging HIPAA event."""
        compliance = ComplianceLogger(audit_logger)

        event_id = compliance.log_hipaa_event(
            "patient.record.access",
            patient_id="P12345",
            phi_accessed=True,
        )

        assert event_id.startswith("evt_")

    def test_log_soc2_event(self, audit_logger: AuditLogger) -> None:
        """Test logging SOC2 event."""
        compliance = ComplianceLogger(audit_logger)

        event_id = compliance.log_soc2_event(
            "security.control.verified",
            control_id="CC6.1",
        )

        assert event_id.startswith("evt_")

    def test_generate_compliance_report(self, audit_logger: AuditLogger) -> None:
        """Test generating compliance report."""
        compliance = ComplianceLogger(audit_logger)

        # Log some GDPR events
        compliance.log_gdpr_event("data.access", subject_id="user123")
        compliance.log_gdpr_event("data.deletion", subject_id="user456")

        # Generate report
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow() + timedelta(days=1)

        report = compliance.generate_compliance_report("GDPR", start_date, end_date)

        assert report["framework"] == "GDPR"
        assert report["total_events"] >= 2
        assert "events_by_type" in report
        assert "events_by_severity" in report
