# Feature Specification: Production Hardening

**Feature Branch**: `[402-production-hardening]`  
**Created**: 2026-08-25  
**Status**: Draft  
**Input**: User description: "Work on the requirements for OPS-402, Production Hardening: rate limiting, caching policy, and operational alerts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Protect shared capacity (Priority: P1)

As an MCP client user, I receive a clear, temporary capacity response when my request volume exceeds the published allowance, so that one caller cannot exhaust service capacity or upstream quota for other users.

**Why this priority**: Admission control is the immediate protection against accidental loops and abusive traffic, and it protects both client reliability and the shared YouTube quota.

**Independent Test**: Send requests from two distinct caller identities until one exceeds the configured allowance; verify that only the over-limit caller is temporarily rejected while the other can still complete an eligible request.

**Acceptance Scenarios**:

1. **Given** a caller is within its allowance, **When** it invokes an eligible MCP tool, **Then** the request is processed normally.
2. **Given** a caller has consumed its allowance, **When** it invokes another eligible MCP tool during the same enforcement period, **Then** it receives a safe, retryable capacity response that states when it may retry and no upstream request is made.
3. **Given** one caller has exceeded its allowance, **When** a different identified caller invokes an eligible MCP tool, **Then** the second caller's allowance is evaluated independently.

---

### User Story 2 - Reuse safe read results (Priority: P2)

As an MCP client user, I receive a recent result for repeatable public read requests without avoidable repeat work, so that common research workflows remain responsive and conserve shared upstream quota.

**Why this priority**: Safe reuse improves the primary read experience and reduces avoidable load, but must never compromise freshness, authorization, or mutation correctness.

**Independent Test**: Invoke the same documented cacheable public read request twice within its freshness period and verify that the second result is equivalent to the first without a second upstream execution; verify that a mutation and an access-sensitive request never reuse that result.

**Acceptance Scenarios**:

1. **Given** a cacheable public read request has completed successfully, **When** an equivalent request arrives within its freshness period, **Then** the caller receives the prior successful result with an indication that it was reused.
2. **Given** the freshness period has ended or the request differs in a result-affecting input or access context, **When** the request arrives, **Then** it is evaluated as a new request.
3. **Given** a request changes data, depends on caller-specific authorization, or returns an error, **When** it completes, **Then** its outcome is not made available for later reuse.

---

### User Story 3 - Respond to sustained degradation (Priority: P3)

As an operator, I receive actionable, deduplicated alerts for sustained error-rate or latency degradation and a recovery signal when normal operation resumes, so that I can investigate service incidents before they materially affect users.

**Why this priority**: Operators need prompt, trustworthy signals to meet the service reliability target; alert quality matters because repeated noise delays response.

**Independent Test**: Feed controlled request outcomes that cross and then clear the error-rate and latency thresholds; verify one alert per incident, a safe diagnostic context, and one recovery notification after sustained normalization.

**Acceptance Scenarios**:

1. **Given** the service receives at least 20 eligible requests in a rolling 10-minute period, **When** 5% or more of those requests fail with service, capacity, or upstream failures, **Then** the designated operator is alerted within 5 minutes.
2. **Given** at least 20 eligible requests in a rolling 10-minute period, **When** the 95th-percentile latency exceeds 3 seconds for simple or cached calls or 8 seconds for transcript-heavy calls, **Then** the designated operator is alerted within 5 minutes.
3. **Given** an alerting condition remains active, **When** additional evaluation periods breach the same condition, **Then** the system does not send duplicate incident notifications; when the condition remains normal for 15 consecutive minutes, it sends one recovery notification.

### Edge Cases

- A request has no trustworthy caller identity: it is evaluated against a separate conservative anonymous allowance so that missing identity cannot bypass limits or merge unrelated authenticated callers.
- The rate-limit or result-reuse decision cannot be evaluated: the request fails safely with an actionable temporary-service response rather than bypassing the protection or returning an unverified stored result.
- A request is retried after a capacity rejection: it is evaluated again against the current allowance; it is not treated as a successful tool invocation and must not trigger upstream work while still rejected.
- A cached result expires while a refresh attempt fails: the expired result is not returned as current; the caller receives the normalized failure from the new evaluation.
- The same parameters are used under different authorization capabilities: no result is reused across those contexts.
- A tool mutates data after related read results were reused: all cached entries identified by the documented invalidation policy for that resource are removed before the mutation is reported as successful.
- Low request volume causes a brief error or latency outlier: it is visible in operational measurements but does not create a sustained-degradation alert until the minimum sample size and duration are met.
- The alert-delivery destination is unavailable: the failed delivery is recorded for operator review without exposing contact or secret configuration, and the active incident remains eligible for the next delivery attempt.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for normal, exhausted, and independent caller allowances; cache hit, expiry, isolation, invalidation, and failure behavior; and each alert threshold, suppression, recovery, and delivery-failure path. Add contract tests proving that all client-facing capacity and temporary-service outcomes remain safe MCP errors and that no rejected request invokes an upstream operation.
- **Green**: Add the smallest policy-controlled admission, result-reuse, telemetry, and alert behavior required for the above tests to pass. Demonstrate the documented defaults: 60 eligible tool invocations per identified caller per rolling minute, a separate 10-invocation-per-minute anonymous allowance, and a five-minute maximum freshness period for approved public read results.
- **Refactor**: Consolidate shared policy evaluation and bounded operational classifications; remove duplicated cache eligibility and alert-threshold logic; preserve existing MCP success and error contracts; and run the full repository test suite after all changes.
- **Required test levels**: unit tests for policy boundaries and classification, integration tests for public request handling and upstream-work suppression, contract tests for client-visible outcomes, and controlled operational tests for alert lifecycle and notification failure. A production alert destination is not required for automated verification.
- **Python docstrings**: Every new or changed Python function in scope MUST include or retain a complete reStructuredText docstring that covers its purpose, arguments, result, errors, and relevant side effects, including whether it can reject a request, reuse a result, or emit an operational signal.
- **Pull-request evidence**: Review evidence MUST include targeted passing tests for all three stories, controlled evidence for one accepted and one rejected request, one cache hit and one required refresh, one alert and recovery sequence, and a passing full-suite run using `PYTHONPATH=src python3 -m pytest`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The service MUST enforce a documented, configurable admission allowance before eligible public MCP tool invocations begin upstream execution.
- **FR-002**: The default admission allowance MUST permit no more than 60 eligible tool invocations per identified caller in any rolling one-minute period and MUST permit no more than 10 eligible tool invocations from the anonymous caller category in that period.
- **FR-003**: The service MUST determine allowance independently for each trustworthy caller identity and MUST place requests without a trustworthy identity in the anonymous category; it MUST NOT use raw secrets, full request bodies, or unbounded user-provided values as an identity or operational dimension.
- **FR-004**: When an invocation exceeds its allowance, the service MUST reject it before upstream execution with a safe, retryable MCP capacity error that includes a retry-after indication and excludes credentials, internal policy state, and other callers' information.
- **FR-005**: The service MUST apply admission control consistently to all public MCP tool invocations, including read, mutation, upload, and transcript-related tools, while allowing liveness and readiness checks to remain available for platform operations.
- **FR-006**: The service MUST publish a cache policy that identifies each public tool or tool class as either eligible or ineligible for result reuse, states the maximum freshness period, and defines the invalidation event or reason for ineligibility.
- **FR-007**: Only successful, public, read-only, deterministic tool results that the cache policy explicitly marks eligible MAY be reused; errors, partial failures, mutations, uploads, deletions, ratings, moderation actions, owner-scoped results, and authorization-sensitive results MUST NOT be reused.
- **FR-008**: The maximum freshness period for an approved public read result MUST be five minutes unless a stricter documented period is required by the tool's data-freshness expectation.
- **FR-009**: A reusable result MUST be isolated by the normalized request inputs, tool version, and access context that could change the returned data; a result MUST NOT be shared across different authorization capabilities or callers when that could reveal different data.
- **FR-010**: Before reporting a successful mutation, the service MUST remove all reusable results identified by the documented invalidation policy as related to the changed resource.
- **FR-011**: The service MUST make cache reuse observable through bounded aggregate measurements that distinguish eligible requests, reused results, fresh evaluations, expirations, invalidations, and reuse-decision failures without recording result contents, credentials, or user-supplied high-cardinality values.
- **FR-012**: The service MUST record bounded operational measurements for eligible request volume, successful and failed outcomes, capacity rejections, and latency by endpoint and documented tool class, preserving existing request correlation.
- **FR-013**: The service MUST create an operator alert when, in a rolling 10-minute period with at least 20 eligible requests, the service/upstream/capacity failure rate is at least 5%, and MUST notify the designated operator within 5 minutes of detection.
- **FR-014**: The service MUST create an operator alert when, in a rolling 10-minute period with at least 20 eligible requests, 95th-percentile latency exceeds 3 seconds for documented simple or cached calls or 8 seconds for documented transcript-heavy calls, and MUST notify the designated operator within 5 minutes of detection.
- **FR-015**: Alert notifications MUST identify the affected service area, alert category, threshold, observed value, evaluation period, and a safe correlation path for investigation; they MUST NOT expose request contents, caller identities, credentials, tokens, or raw upstream payloads.
- **FR-016**: The service MUST deduplicate notifications for a continuing incident and MUST send one recovery notification when the relevant measure remains below its threshold for 15 consecutive minutes.
- **FR-017**: The service MUST record alert-generation and alert-delivery outcomes, including delivery failure, so an operator can determine whether a notification was attempted without revealing notification-destination secrets.
- **FR-018**: The service MUST document the production-hardening defaults, configuration inputs, tool eligibility classifications, alert thresholds, test procedure, and safe operator response procedure, including how to adjust the documented defaults through approved operational configuration.

### Dependencies

- **FND-005 — Health, Logging, Error Model, Metrics**: Provides correlated request observations, normalized client error behavior, and operational measurements used to evaluate and investigate this slice.
- **FND-008 — Deployment and Cloud Observability**: Provides the supported hosted deployment and runtime-observability foundation for configuring and receiving operational alerts.
- **YT-203 through YT-255 and YT-302 through YT-320**: Provide the public tool catalog whose invocation classes and mutation behavior must be covered by the admission and caching policy.

### Scope

**In scope**:

- Per-caller admission protection for every public MCP tool invocation, with safe capacity responses.
- A documented and applied result-reuse policy for safe public read behavior, including expiry, isolation, and mutation invalidation.
- Bounded hardening telemetry and sustained error-rate and latency alerts with recovery notification.
- Operator documentation and deterministic verification for the protections and alerts.

**Out of scope**:

- New public MCP tools, changes to existing tool inputs or successful result shapes, and catalog-wide public-route coverage (OPS-403).
- Credential-gated live verification matrices and real YouTube smoke execution (OPS-404).
- Changes to YouTube quota pricing, upstream retry policy, OAuth capability lifecycle, or the underlying identity/authentication strategy.
- Caching of personalized, authorization-sensitive, mutation, media, error, partial, or stale results.
- Manual incident response staffing, on-call rotations, or an organization-wide notification escalation policy beyond the designated operational alert destination.

### Assumptions

- The hosted environment supplies an approved configuration path for the documented allowance values, cache policy values, alert destination, and alert enablement without embedding secrets in source control.
- Existing request authentication or trusted gateway context can provide a stable caller identity when one is available; the anonymous allowance protects the service when it is not.
- “Eligible request” excludes liveness/readiness probes and requests rejected before the service can assign an applicable public-tool class; all accepted public MCP tool invocations are eligible.
- A simple or cached call is a documented public read class that does not perform transcript retrieval; transcript-heavy calls are the documented transcript/caption retrieval and processing classes. Every default public tool will receive one of these documented classes before rollout.
- Five minutes balances utility and freshness for public research reads; tool owners may set a lower documented period but cannot set a longer one in this slice.
- Existing safe MCP error categories can represent temporary capacity and temporary-service outcomes without adding a new successful response shape.

### Key Entities *(include if feature involves data)*

- **Caller allowance**: The bounded count of eligible public tool invocations assigned to one identified or anonymous caller during the current rolling enforcement period.
- **Cache policy entry**: The documented classification of a public tool or tool class, including reuse eligibility, maximum freshness period, isolation criteria, and invalidation event or ineligibility reason.
- **Reusable result**: A successful public read result that remains within its documented freshness period and isolation boundary.
- **Operational measurement**: A bounded aggregate observation of request volume, outcome, capacity rejection, reuse decision, or latency used for reliability evaluation.
- **Alert incident**: One sustained error-rate or latency condition, its safe diagnostic context, notification state, and recovery state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In controlled admission tests, 100% of over-limit invocations are rejected before upstream execution, include a retry-after indication, and do not prevent a separate within-limit caller from completing its request.
- **SC-002**: In controlled repeat-read tests, 100% of documented cacheable requests within their freshness period reuse an equivalent eligible result, while 100% of expired, access-sensitive, mutation, and error cases require a fresh evaluation or return the current failure.
- **SC-003**: In controlled mutation tests, 100% of cache entries identified by the documented invalidation policy are unavailable for reuse after a successful mutation.
- **SC-004**: In controlled sustained-degradation tests meeting the minimum sample size, 100% of error-rate and latency threshold breaches generate one operator alert within 5 minutes, and 100% of incidents that remain normal for 15 minutes generate one recovery notification.
- **SC-005**: In controlled low-volume and continuing-incident tests, 0 false sustained-degradation alerts are generated below the 20-request minimum and no duplicate notification is sent for a single active incident.
- **SC-006**: During an incident exercise, an operator can identify the affected service area, threshold, observed measurement, evaluation period, and correlated safe diagnostic records within 5 minutes without accessing credentials or request content.
- **SC-007**: The service maintains the PRD's 99.5% monthly availability target and its p95 latency targets of under 3 seconds for simple/cached calls and under 8 seconds for transcript-heavy calls, excluding requests explicitly rejected by admission control.
