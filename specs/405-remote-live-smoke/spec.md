# Feature Specification: Layer 4 Remote MCP Read-Only Live Smoke

**Feature Branch**: `[405-remote-live-smoke]`  
**Created**: 2026-08-26  
**Status**: Draft  
**Input**: User description: "Work on the requirements for OPS-405, Layer 4 Remote MCP Read-Only Live Smoke."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a Remote Read-Only Smoke (Priority: P1)

An approved operator can explicitly run a credential-gated smoke workflow against a running remote MCP server. The workflow initializes a session, discovers the server's live catalog, and invokes every discovered tool that is on the reviewed read-only allowlist using its approved public reference input.

**Why this priority**: This is the feature's core value: proving that a deployed endpoint, its authentication and session behavior, selected handlers, and the live YouTube path work together without performing a write.

**Independent Test**: Run the workflow against a controlled remote responder and verify the initialization, catalog discovery, selected calls, session continuity, and one reported outcome for every selected tool.

**Acceptance Scenarios**:

1. **Given** the operator has explicitly enabled the live smoke and supplied a remote endpoint and the required authentication material, **When** the workflow runs, **Then** it initializes the remote MCP session, discovers the remote catalog, and calls each discovered allowlisted tool through the public transport.
2. **Given** the remote catalog contains an approved read-only tool with a reviewed public fixture, **When** the workflow invokes it, **Then** the workflow reports that tool's successful structured result, documented safe availability error, or actionable failure separately.
3. **Given** a remote transport requires a session continuation value, **When** initialization succeeds, **Then** catalog discovery and every selected call use that session as required by the remote transport.

---

### User Story 2 - Prevent Unsafe Live Calls (Priority: P1)

As a security reviewer, I can confirm that the remote workflow selects tools only from a reviewed explicit allowlist and does not expose credentials or sensitive request and response data in its output or evidence.

**Why this priority**: A live verification workflow must be safe to run against staging or production and must not become a path for accidental mutations, credential disclosure, or uncontrolled data collection.

**Independent Test**: Provide a catalog containing allowlisted, unapproved, mutation-capable, and sensitive operations, then verify the workflow invokes only the approved entries and that its recorded output contains no credential-bearing values, raw headers, inputs, or upstream response bodies.

**Acceptance Scenarios**:

1. **Given** the discovered catalog contains a tool absent from the explicit allowlist, **When** the workflow evaluates the catalog, **Then** it reports the tool as intentionally excluded and never invokes it.
2. **Given** an operator omits the enablement flag, remote endpoint, or required authentication material, **When** the workflow is started, **Then** it stops before making a remote call and provides a clear message that does not reveal supplied secret values.
3. **Given** a successful live tool result includes endpoint identity, **When** the workflow reports the result, **Then** it verifies that identity agrees with the discovered tool's published upstream operation identity.

---

### User Story 3 - Interpret and Reproduce Verification Evidence (Priority: P2)

As a maintainer, I can review a bounded, credential-safe report to see what was selected, excluded, successful, safely unavailable, or failed, and can distinguish this manual remote verification from deterministic catalog checks, configured-runtime checks, and the local live smoke.

**Why this priority**: Clear evidence makes a failed production verification actionable while preserving the boundary that external credentials, quota, and upstream availability make this unsuitable for ordinary automation.

**Independent Test**: Complete a run with a mix of successful, safely unavailable, excluded, timed-out, and failed tools, then verify the report classifies each result without exposing sensitive values and the operator documentation identifies the appropriate verification workflow.

**Acceptance Scenarios**:

1. **Given** one selected tool times out or returns an unexpected result, **When** the workflow completes, **Then** it records an actionable failure for that tool and continues reporting the other selected tools within the configured request limit.
2. **Given** an operator is choosing a verification workflow, **When** they consult the operator documentation, **Then** they can identify the purpose, prerequisites, safety boundary, and quota/upstream implications of remote live smoke versus the other verification paths.

### Edge Cases

- The enablement flag, endpoint, or required server authentication material is missing, malformed, or rejected; the workflow fails closed before a live tool call and redacts sensitive values.
- Initialization fails, returns no usable continuation value when one is required, or the session expires before discovery or a selected call; the report identifies the affected stage and does not substitute a local server.
- The catalog is empty, contains no allowlisted tools, or changes after discovery; the workflow reports the selection outcome and does not call an unselected or newly appearing tool.
- An allowlisted tool has no reviewed public fixture, its fixture cannot be used safely, or the discovered metadata lacks a required operation identity; the tool is not invoked and receives an actionable report outcome.
- A selected tool returns an expected public-data availability error, times out, or returns a result whose endpoint identity conflicts with discovery metadata; the report classifies the condition per tool without emitting raw bodies.
- The remote catalog contains write-capable, OAuth-required, owner-only, credential-sensitive, upload, download, rating, abuse-report, moderation, subscription, retrieval, or baseline-server operations; each is excluded regardless of its name or read-like metadata.
- The run reaches its approved request-count or time limit; remaining selected tools are reported as not attempted due to the bound rather than retried without limit.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with deterministic failing tests for the remote workflow using a controlled remote MCP responder. Cover prerequisite gating, initialization and continuation handling, `tools/list` discovery, `tools/call` construction, explicit allowlist filtering, excluded-tool reporting, per-tool classifications, operation-identity agreement, request/time bounds, and redaction. Add failing documentation checks for the required workflow distinction and safety guidance.
- **Green**: Implement only the behavior required for the controlled responder tests and the manually enabled remote live command: it must connect through the public remote transport, use reviewed public fixtures for selected tools, and produce bounded redacted evidence. It must make no in-process substitute for the target server.
- **Refactor**: Consolidate shared verification and redaction rules while retaining the explicit allowlist and reviewed fixtures as independently auditable artifacts. After focused tests pass, run the existing catalog and configured-runtime suites plus the complete repository suite with `make test`; require a passing result before review. Run the real remote live smoke only after an approved deployment and never as a pull-request or deployment gate.
- **Required test levels**: Unit tests for selection, classification, bounds, and redaction; transport integration tests with a controlled remote responder; contract tests for public MCP initialization, discovery, calls, and session behavior; documentation verification; and a manually triggered end-to-end live smoke against an approved remote endpoint.
- **Python documentation**: Every new or changed Python function in scope must have or update a reStructuredText docstring that states its purpose, inputs, return behavior, externally visible errors, and credential/redaction obligations where applicable.
- **Review evidence**: Provide the focused remote-smoke test result, `make test-tools`, `make test-runtime`, and a passing `make test` result. If the optional remote live smoke is run, attach its redacted operator report only; do not attach credentials, request headers, inputs, or raw response bodies.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an operator-triggered remote live smoke workflow that requires an explicit enablement flag, a configured remote MCP endpoint, and the authentication material required by that endpoint.
- **FR-002**: The workflow MUST fail closed before making a remote request when a prerequisite in FR-001 is missing, unusable, or rejected, and its message MUST state the missing prerequisite without revealing secret values.
- **FR-003**: The workflow MUST connect to the already running target through its public MCP transport, initialize a session, retain and use any continuation information required by that transport, discover the active catalog through `tools/list`, and invoke eligible tools through `tools/call`.
- **FR-004**: The workflow MUST NOT replace the target connection with an in-process application, dispatcher, fixture result, or controlled local transport.
- **FR-005**: The workflow MUST select tools exclusively from a reviewed, explicit allowlist of documented public operations that are both API-key-capable and read-only, and MUST use a reviewed live-safe public reference input for every selected tool.
- **FR-006**: The workflow MUST NOT infer eligibility from a tool name, a `list` suffix, or generic read-like metadata.
- **FR-007**: The allowlist MUST exclude all create, update, delete, upload, download, rating, abuse-report, moderation, subscription, OAuth-required, owner-only, credential-sensitive, retrieval, and baseline-server operations.
- **FR-008**: For every discovered tool not on the allowlist, the workflow MUST report an intentional exclusion and MUST NOT invoke that tool.
- **FR-009**: The workflow MUST produce one terminal outcome for every selected discovered tool: successful structured MCP content, a documented safe availability error, actionable failure, or not attempted because an approved run bound was reached.
- **FR-010**: When a successful endpoint-backed result exposes an endpoint identity, the workflow MUST verify it matches that tool's discovery metadata upstream operation identity and report a mismatch as an actionable failure.
- **FR-011**: The workflow MUST enforce documented maximum request-count and elapsed-time bounds and MUST report a bounded, per-tool status rather than retrying without limit.
- **FR-012**: Console output and persisted evidence MUST redact MCP credentials, YouTube credentials, authorization values, request secrets, raw request headers, request inputs, and full upstream response bodies.
- **FR-013**: The workflow MUST be opt-in and excluded from ordinary pull-request checks, the complete test suite, quality checks, and automated hosted deployment gates.
- **FR-014**: Operator documentation MUST explain how to authorize and run the workflow, the required endpoint and authentication prerequisites, the approved deployment boundary, expected evidence, and the quota and upstream-availability implications.
- **FR-015**: Operator documentation MUST distinguish this remote live smoke from deterministic catalog verification, configured-runtime verification, and local live smoke, including the purpose and safety boundary of each.

### Key Entities *(include if feature involves data)*

- **Remote smoke run**: One explicitly authorized verification attempt, including its target endpoint identity, prerequisite status, bounds, aggregate outcome, and redacted evidence.
- **Reviewed allowlist entry**: The auditable approval for one public tool, including its tool identity, reason it is live-safe and read-only, and its reviewed public reference input.
- **Discovered tool**: A tool advertised by the target server's active catalog, including its identity and published upstream operation identity when available.
- **Per-tool outcome**: The terminal classification for a selected or excluded discovered tool, including status, safe reason or actionable failure summary, and no sensitive payload data.
- **Remote session**: The initialization context and any continuation information required to make discovery and tool calls to the same remote server.

## Assumptions

- Approved operators obtain endpoint authorization and any required credentials through the existing operational process before starting the workflow.
- Public reference inputs are reviewed for live safety and remain bounded, non-owner-specific, and suitable for staging or production verification.
- A documented safe availability error represents public data that cannot safely be returned or is temporarily unavailable; it is distinct from an unexpected workflow failure.
- Upstream availability and quota consumption can make a live run incomplete; the workflow's value is accurate per-tool evidence, not a guarantee that every upstream call succeeds.

## Dependencies

- Remote MCP transport, protocol, security, and hosted reachability foundations: `FND-009`, `FND-010`, `FND-013`, and `FND-021`.
- Configured live YouTube execution capability and its resource-family coverage: `YT-157`, `YT-158`, `YT-159`, and `YT-160`.
- Deterministic catalog coverage and configured-runtime verification that this workflow complements: `OPS-403` and `OPS-404`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a controlled remote-transport test containing approved and unapproved catalog entries, 100% of approved discovered entries are selected only when they have a reviewed fixture, and 100% of all unapproved entries are reported as excluded without a call.
- **SC-002**: For every completed smoke run, the operator receives exactly one terminal report entry for 100% of selected discovered tools, including success, documented safe availability, actionable failure, or bound-reached status.
- **SC-003**: In verification tests that supply credential values, headers, request secrets, inputs, and full upstream bodies, 0 such raw values appear in console output or persisted evidence.
- **SC-004**: A run with a controlled delayed or failing selected tool completes within its documented total time bound and reports the affected tool without exceeding its documented maximum request count.
- **SC-005**: In an operator walkthrough using the documentation, at least 90% of participating approved operators can correctly identify the remote smoke's prerequisites, opt-in boundary, and difference from catalog, configured-runtime, and local live verification before running it.
- **SC-006**: In a successful live result that publishes endpoint identity, 100% of selected-tool reports either confirm agreement with the discovered operation identity or classify the mismatch as an actionable failure.
