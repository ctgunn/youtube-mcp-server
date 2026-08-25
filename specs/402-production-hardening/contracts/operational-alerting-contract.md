# Operational Alerting Contract

## Scope

This contract defines the production operator interface for OPS-402. It does not expose new MCP tools or client-visible result fields. It uses bounded application observations and Terraform-managed GCP logging/monitoring resources to create, deduplicate, close, and audit sustained-degradation incidents.

## Safe Operational Event Dimensions

Eligible public tool calls emit only the following bounded classifications for production hardening:

| Field | Allowed values |
| --- | --- |
| `endpoint` | `/mcp` |
| `toolClass` | `simple_cached`, `transcript_heavy` |
| `outcome` | `success`, `service_failure`, `upstream_failure`, `capacity_rejection`, `client_failure` |
| `cacheStatus` | `hit`, `miss`, `bypass` |
| `incidentCondition` | `sustained_error_rate`, `simple_latency`, `transcript_latency` |
| `incidentState` | `normal`, `active`, `recovering`, `delivery_failed` |

Events and metric labels MUST NOT contain request IDs, caller identities, token fingerprints, raw tool names when the class is sufficient, input arguments, result content, headers, credentials, notification endpoints, or raw upstream payloads.

## Alert Conditions

All conditions use a rolling 10-minute evaluation window and require at least 20 eligible requests. Missing data is not a recovery signal.

| Condition | Trigger | Notification target |
| --- | --- | --- |
| Sustained error rate | At least 5% of eligible calls are `service_failure`, `upstream_failure`, or `capacity_rejection`. | Designated operator within 5 minutes of detection. |
| Simple/cached latency | Eligible `simple_cached` call p95 exceeds 3000 ms. | Designated operator within 5 minutes of detection. |
| Transcript latency | Eligible `transcript_heavy` call p95 exceeds 8000 ms. | Designated operator within 5 minutes of detection. |

An alert opens one incident for a condition/service area. Continuing breaches do not produce duplicate open notifications. After the first normal eligible observation, the incident enters recovery; any renewed breach returns it to active. The service emits normal/closure state only after 15 consecutive normal minutes, at which point monitoring sends one recovery notification.

## Infrastructure Inputs and Outputs

Terraform accepts safe, versioned inputs for:

- whether alerting is enabled for the environment;
- alert thresholds and minimum sample count, with the defaults in this contract;
- a list of pre-verified Monitoring notification-channel resource identifiers; and
- service/environment labels and runbook reference used to scope investigation.

Terraform creates log-based metrics for eligible volume, qualified failures, latency/state, and the monitoring policies that consume them. It outputs policy identifiers and metric names for deployment verification. Notification-channel verification and sensitive endpoint configuration remain operator-managed and are not created, logged, or injected into the Cloud Run service.

## Delivery and Investigation

Each open/close policy notification includes affected service area, environment, condition, threshold, observed value, evaluation window, and a runbook/correlation reference. Platform monitoring is the authoritative delivery/audit system. Application event generation and platform delivery failures are recorded as safe operational outcomes; neither leaks destination configuration or secrets.

## Contract Validation

Tests must assert metric filter/classification boundaries, condition thresholds, minimum sample count, policy/service/environment scope, notification-channel attachment, open-notification deduplication, recovery after 15 normal minutes, missing-data behavior, and redaction. Terraform formatting and validation plus a non-production policy/incident exercise provide deployment evidence; CI never requires receipt at a production notification destination.
