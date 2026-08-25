# Production hardening alert response

Use this runbook when the hosted YouTube MCP service reports sustained errors,
elevated simple-tool latency, or elevated transcript-tool latency.

## Immediate assessment

1. Open the related Cloud Monitoring incident and confirm the affected service,
   environment, and bounded condition label.
2. Check the Cloud Run service revision, request volume, error events, and
   latency in the same time window.
3. Check Redis connectivity and the availability of the upstream YouTube
   service before changing traffic or capacity.

## Condition-specific response

### `sustained_error_rate`

Identify whether failures are categorized as upstream, service, or capacity
rejections. For upstream failures, check the upstream status and quota limits.
For service failures, inspect the current Cloud Run revision logs and roll back
to the most recent healthy revision if a release correlates with the incident.
For capacity rejections, temporarily reduce nonessential traffic or raise the
reviewed capacity limits through the normal infrastructure change process.

### `simple_latency` or `transcript_latency`

Check Cloud Run request latency, Redis latency, and upstream response latency.
Compare the active revision to the previous healthy revision. Do not increase
limits or disable rate limiting solely to clear an alert; address the source of
the latency first.

## Recovery and escalation

The application holds recovery until 15 minutes of normal eligible
observations. Confirm the incident closes and that the staging notification
channel receives the closure message. Escalate to the service owner when the
condition persists beyond 30 minutes or recurs after a rollback.

## Safety

Do not place credentials, bearer tokens, request payloads, or customer data in
the incident, ticket, or runbook updates.
