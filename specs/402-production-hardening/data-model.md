# Data Model: Production Hardening

## Caller Identity

| Field | Description | Validation |
| --- | --- | --- |
| `caller_class` | Finite category: `identified` or `anonymous`. | Never derived from a raw user-controlled header. |
| `internal_key` | Non-reversible internal admission key for an identified caller. | Never emitted in logs, metrics, errors, cache keys, or responses. |
| `identity_source` | `trusted_gateway`, `validated_credential`, or `none`. | Gateway source is permitted only with explicit deployment trust configuration. |

One caller identity owns zero or more admission decisions. A shared credential represents one identified allowance unless the trusted identity source provides a distinct principal.

## Admission Policy and Decision

| Field | Description | Validation |
| --- | --- | --- |
| `policy_version` | Version separating admission behavior and stored records. | Non-empty, bounded configuration value. |
| `window_seconds` | Rolling admission period. | Positive integer; default 60. |
| `identified_limit` | Maximum valid tool calls for one identified caller in the window. | Positive integer; default 60. |
| `anonymous_limit` | Maximum valid tool calls for the anonymous class in the window. | Positive integer; default 10. |
| `decision` | `accepted`, `rejected`, or `decision_failure`. | Only accepted calls enter dispatch. |
| `retry_after_seconds` | Earliest bounded retry delay for a rejected call. | Present only for `rejected`; positive integer. |
| `observed_at` | Time the policy decision was made. | Used only for expiry/window evaluation. |

**Transitions**: `candidate` → `accepted` (one admission recorded); `candidate` → `rejected` (no dispatch); `candidate` → `decision_failure` (safe temporary-service failure, no dispatch). Expired accepted records leave the rolling window automatically.

## Cache Policy Entry

| Field | Description | Validation |
| --- | --- | --- |
| `tool_name` | Public tool selected for policy evaluation. | Must match a registered default tool. |
| `eligibility` | `eligible` or `ineligible`. | Ineligible reason required when false. |
| `tool_class` | Finite operational class: `simple_cached` or `transcript_heavy`. | Every eligible default tool has one class; transcript/caption classes are transcript-heavy. |
| `max_freshness_seconds` | Maximum time a successful result can be reused. | Positive integer no greater than 300 for eligible entries. |
| `required_public_selectors` | Input requirements for an eligible variant. | Must reject owner, moderation, delegation, media, and sensitive selectors. |
| `invalidation_relations` | Resource identifiers that invalidate matching eligible results after mutation. | Explicit finite mapping; absence produces a recorded safe no-op reason. |

## Reusable Result

| Field | Description | Validation |
| --- | --- | --- |
| `cache_key` | Internal identity generated from policy/catalog revision, tool, and canonical validated public arguments. | Never includes secret, session, caller, request ID, raw payload, or result content in logs/metrics. |
| `result` | Complete successful tool result available for reuse. | Errors, partial results, stale data, and sensitive results are never stored. |
| `created_at` / `expires_at` | Reuse lifetime. | `expires_at` must not exceed the matching policy’s 300-second maximum. |
| `status` | `fresh`, `expired`, or `invalidated`. | Only `fresh` entries can be returned. |
| `policy_version` / `catalog_revision` | Compatibility boundary for stored result. | Difference causes a cache miss; namespace rotation handles broad changes. |

**Transitions**: `eligible fresh invocation` → `fresh`; `fresh` → `expired` by time; `fresh` → `invalidated` before a related successful mutation response. A failed mutation leaves existing entries unchanged. A refresh failure never restores or returns an expired entry.

## Operational Sample

| Field | Description | Validation |
| --- | --- | --- |
| `observed_at` | Request-completion time. | Retained only for the bounded alert window. |
| `endpoint` | Safe endpoint category. | Public tool alerts use `/mcp`; health/readiness excluded. |
| `tool_class` | `simple_cached` or `transcript_heavy`. | Finite declared value; never a raw tool argument. |
| `outcome` | `success`, `service_failure`, `upstream_failure`, `capacity_rejection`, or `client_failure`. | Error ratio includes service, upstream, and capacity only. |
| `latency_ms` | Non-negative request latency. | Used for p95 only after the 20-sample minimum. |
| `cache_status` | `hit`, `miss`, or `bypass`. | Bounded observability dimension only. |

## Alert Incident

| Field | Description | Validation |
| --- | --- | --- |
| `incident_key` | Finite service-area plus condition identity. | Never includes caller, tool arguments, request IDs, or payload. |
| `condition` | `sustained_error_rate`, `simple_latency`, or `transcript_latency`. | One active incident per condition/service area. |
| `window_start` / `window_end` | Current 10-minute evaluation period. | Requires at least 20 eligible samples. |
| `threshold` / `observed_value` | Triggered policy value and current safe measurement. | Error threshold: 5%; simple p95: 3000 ms; transcript p95: 8000 ms. |
| `state` | `normal`, `active`, `recovering`, or `delivery_failed`. | Active is deduplicated; recovery only after 15 normal minutes. |
| `normal_since` | First continuously normal eligible observation after an active incident. | Reset by a new breach. |
| `delivery_state` | `not_attempted`, `open_recorded`, `close_recorded`, or `delivery_failed`. | Destination credentials never appear in entity data or application logs. |

**Transitions**: `normal` → `active` when a qualified window breaches; `active` → `recovering` at the first normal eligible observation; `recovering` → `active` on a new breach; `recovering` → `normal` only after 15 consecutive normal minutes. Platform monitoring opens on active state and closes only when the delayed normal state is emitted.

## Relationships

- A **Caller Identity** is evaluated by one **Admission Policy** and produces one **Admission Decision** per valid tool call.
- An accepted decision may evaluate one **Cache Policy Entry**; an eligible fresh request can create one **Reusable Result**.
- A successful mutation invalidates only the **Reusable Results** selected by its matching policy relation.
- Each eligible completed call emits one **Operational Sample**; a bounded group of samples evaluates one **Alert Incident** condition.
- The alert incident state is represented by platform monitoring resources, which deliver configured operator notifications and record delivery/audit outcomes.
