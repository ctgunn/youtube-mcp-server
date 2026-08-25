resource "google_logging_metric" "mcp_hardening_incident" {
  name        = "mcp_hardening_incident"
  description = "Bounded application incident-state events for the MCP service."

  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.event=\"hardening.alert_incident\""

  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "INT64"
    unit        = "1"

    labels {
      key         = "condition"
      value_type  = "STRING"
      description = "Finite sustained error or latency condition."
    }
  }

  label_extractors = {
    "condition" = "EXTRACT(jsonPayload.condition)"
  }

  value_extractor = "EXTRACT(jsonPayload.observedValue)"
}

resource "google_monitoring_alert_policy" "mcp_hardening_incident" {
  count        = var.alerting_enabled ? 1 : 0
  display_name = "${var.service_name} ${var.environment} MCP sustained degradation"
  combiner     = "OR"

  conditions {
    display_name = "MCP bounded incident state is active"

    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/mcp_hardening_incident\" AND resource.type=\"cloud_run_revision\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  notification_channels = var.alert_notification_channel_ids

  documentation {
    content   = "Investigate bounded MCP incident state using the production-hardening runbook. ${var.alert_runbook_url}"
    mime_type = "text/markdown"
  }
}
