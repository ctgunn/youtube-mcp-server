"""Static contract checks for production-hardening monitoring assets."""

from __future__ import annotations

from pathlib import Path


def test_monitoring_policy_uses_bounded_incident_metric_and_operator_channels():
    """Require Terraform to bind the application incident state to Monitoring."""
    content = Path("infrastructure/gcp/monitoring.tf").read_text()

    assert "google_logging_metric" in content
    assert "hardening.alert_incident" in content
    assert "google_monitoring_alert_policy" in content
    assert "alert_notification_channel_ids" in content
