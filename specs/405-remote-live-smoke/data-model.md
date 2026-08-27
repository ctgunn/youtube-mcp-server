# Data Model: Layer 4 Remote MCP Read-Only Live Smoke

## Remote Smoke Run

Represents one explicitly authorized attempt to verify a running remote MCP server.

| Field | Description | Validation |
| --- | --- | --- |
| `runId` | Local safe identifier for the verification attempt. | Non-empty; contains no endpoint, credential, or session value. |
| `target` | Approved remote endpoint identity used only for connection. | Required before network activity; never copied into evidence as a full URL or query. |
| `authorizationState` | Whether enablement, endpoint, and endpoint-required authentication were present. | `authorized` only when every prerequisite is satisfied; otherwise run fails closed. |
| `protocolVersion` | Version negotiated by successful initialization. | Retained for continuation requests; omitted from evidence if absent or malformed. |
| `requestCount` | Number of remote protocol POSTs attempted. | At most 14: initialization, discovery, and at most 12 calls. |
| `toolCallLimit` | Approved selected tool-call maximum. | Fixed positive maximum of 12. |
| `outcomes` | Per-tool terminal entries. | Exactly one entry for every selected discovered tool; exclusions are separately recorded. |
| `overallStatus` | Aggregate operator result. | Passed only if all selected outcomes succeed; otherwise safe-error or failed completion. |

**State transitions**: `created` → `preflight_failed` or `authorized` → `initialized` → `catalog_discovered` → `calling` → `completed`. A transport/protocol failure transitions to `completed` with a fixed safe failure category; no transition retries without the documented bounds.

## Reviewed Allowlist Entry

Represents one auditable approval to make a live read-only tool call.

| Field | Description | Validation |
| --- | --- | --- |
| `toolName` | Public MCP tool identity. | Non-empty; explicit active entry only; must be present in discovery before invocation. |
| `arguments` | Reviewed public object input. | Object; bounded public selector only; contains no credential, private identifier, raw media, or owner-scoped control. |
| `expectedEndpoint` | Upstream operation identity expected from a success. | Non-empty; must agree with a success result and discovered operation identity when published. |
| `purpose` | Human explanation of safety and smoke value. | Non-empty and reviewable. |
| `fixtureSourceTool` | Earlier approved tool used to derive one bounded public argument, if necessary. | Optional; source must be selected and successful; derived value remains in memory and is never reported. |
| `requestBound` | Tool-call maximum for the entry. | Positive and finite; current entries use one. |
| `timeoutBound` | Maximum acceptable remote request duration. | Positive and no greater than the run's 30-second HTTP limit. |

**State transitions**: `draft` → `reviewed` → `active`; an active entry becomes `not_discovered` if absent from the remote catalog and is not called. Any non-active entry is excluded.

## Discovered Tool

Represents one tool advertised by the target's active `tools/list` result.

| Field | Description | Validation |
| --- | --- | --- |
| `name` | Public tool name. | Non-empty and unique within the discovered catalog. |
| `upstreamOperationKey` | Published upstream operation identity. | Optional; when present, used to validate a selected success result. |
| `selectionState` | Relationship to the approved allowlist. | Exactly `selected` or `excluded`; only active allowlist membership can produce `selected`. |
| `exclusionReason` | Safe reason an unselected tool was not called. | Required for `excluded`; never derived from tool-name heuristics alone. |

**Relationship**: A discovered tool has zero or one reviewed allowlist entry. Every selected discovered tool has one terminal per-tool outcome; every other discovered tool has one exclusion record.

## Remote Session

Represents public transport continuity after a successful initialization.

| Field | Description | Validation |
| --- | --- | --- |
| `sessionPresent` | Whether initialization returned continuation information. | Must be true before discovery/call continuation requests when the target transport requires it. |
| `protocolVersion` | Version accepted by the target. | Must be retained consistently across continuations. |
| `continuationState` | Validity of the session during the run. | `active`, `rejected`, `expired`, or `unknown`; invalid state prevents further calls. |

The session identifier itself is never written to a report, console output, fixture, log assertion, or persisted evidence.

## Per-Tool Outcome

Represents the safe terminal evidence for a selected or excluded discovered tool.

| Field | Description | Validation |
| --- | --- | --- |
| `toolName` | Discovered public tool identity. | References one discovered tool. |
| `selection` | Whether the tool was selected or excluded. | Exactly one of `selected` or `excluded`. |
| `outcome` | Terminal status. | Selected: `success`, `safe_availability_error`, `actionable_failure`, or `bound_reached`; excluded: `excluded`. |
| `safeCategory` | Stable failure/availability classification. | Required for non-success selected outcomes; excludes raw error messages. |
| `endpoint` | Verified endpoint identity. | Present only on safe structured success; matches reviewed/discovered identity when available. |
| `itemCount` | Safe count of returned top-level items. | Optional non-negative integer; never includes item content or identifiers. |
| `summary` | Minimal operator-facing explanation. | Fixed or independently sanitized; contains no secret, header, session, URL/query, argument, or raw body. |

## Redacted Evidence

Represents the only report shape that may cross the CLI/evidence boundary.

| Allowed facts | Prohibited facts |
| --- | --- |
| Tool identity, selection, outcome, safe category, verified endpoint identity, item count, and bounded counts/timings. | MCP/YouTube credentials, authorization values, request headers, session IDs, full endpoint URLs/query strings, request arguments, derived comment identifier, raw errors, exception text, and full upstream response bodies. |
