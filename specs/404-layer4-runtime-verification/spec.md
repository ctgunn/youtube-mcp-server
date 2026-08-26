# Feature Specification: Layer 4 Configured-Runtime Capability and Live-Verification Matrix

**Feature Branch**: `404-layer4-runtime-verification`  
**Created**: 2026-08-26  
**Status**: Draft  
**Input**: User description: "Work on the requirements for OPS-404, as outlined in `requirements/spec-kit-seed.md`."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verify Configured Capability Boundaries (Priority: P1)

As an operator, I can verify which public tools are executable with an API key, require OAuth authorization, or are unavailable in the configured runtime without exposing credentials.

**Why this priority**: Operators need an accurate, safe statement of what the deployed configuration can do before they rely on tools in a workflow.

**Independent Test**: Run the configured-runtime matrix using controlled request observation and confirm that every tool family has a separately reported API-key, OAuth-required, or unavailable-capability outcome.

**Acceptance Scenarios**:

1. **Given** a configured runtime with an API key but no OAuth authorization, **When** the matrix invokes a public API-key-capable tool through MCP, **Then** it reports the documented executable outcome without revealing the credential.
2. **Given** a configured runtime without the OAuth authority required by a public tool, **When** the matrix invokes that tool through MCP, **Then** it reports the documented OAuth-required outcome safely.
3. **Given** required runtime configuration is absent for a tool, **When** the matrix invokes that tool through MCP, **Then** it returns a safe MCP error and does not return representative local data.

---

### User Story 2 - Prove the Live Runtime Boundary (Priority: P2)

As a maintainer, I can prove that configured public tools construct and use the live execution boundary instead of silently falling back to deterministic fixture data.

**Why this priority**: A false local success could hide a configuration or authentication defect until users encounter it in a real workflow.

**Independent Test**: Invoke representative configured tools from every resource family with controlled request observation and verify the recorded live-request intent or documented safe capability error for each case.

**Acceptance Scenarios**:

1. **Given** valid non-secret configuration for a public tool family, **When** the tool is called through MCP, **Then** the matrix observes the expected live-runtime request construction without making a network request.
2. **Given** a configured call cannot proceed because a required capability is unavailable, **When** the tool is called, **Then** the returned MCP error identifies the safe availability boundary rather than presenting representative fixture data as a live result.
3. **Given** a tool family is added to the configured public catalog, **When** the matrix runs, **Then** that family has a configured-runtime case or the run fails with the uncovered family identified.

---

### User Story 3 - Run an Opt-In Read-Only Live Smoke Check (Priority: P3)

As an operator, I can explicitly opt in to a credential-gated live smoke check that exercises only documented public read-only tools and produces credential-safe results.

**Why this priority**: A limited live check gives confidence in real upstream availability while protecting credentials and external YouTube data.

**Independent Test**: With the opt-in flag absent, confirm the live smoke command fails closed; with the flag and valid credentials present, confirm it selects only approved read-only tools and redacts sensitive values from its report.

**Acceptance Scenarios**:

1. **Given** the required opt-in flag is absent, **When** an operator starts the live smoke check, **Then** it does not execute a live request and gives a credential-safe explanation of the prerequisite.
2. **Given** the opt-in flag and required credentials are present, **When** the live smoke check runs, **Then** it invokes only documented public read-only tools using reviewed public inputs.
3. **Given** a tool is mutation-capable, upload-capable, delete-capable, rating-capable, reporting-capable, moderation-capable, or otherwise excluded, **When** the live smoke check selects tools, **Then** it does not invoke that tool.

### Edge Cases

- A tool requires OAuth authorization although an API key is configured; the matrix reports the OAuth-required boundary without attempting an inappropriate call or exposing any credential.
- Configuration is entirely absent or malformed; every affected case returns a safe, actionable MCP error and no representative data is returned.
- The controlled request observer receives an unexpected operation, credential-bearing value, or unbounded request attempt; the configured-runtime case fails and identifies the affected tool safely.
- An upstream live-smoke request times out, is unavailable, or is quota-limited; the smoke report records an actionable per-tool failure without printing request secrets, headers, or full upstream response bodies.
- A proposed live-smoke tool is not explicitly approved as public and read-only; the command excludes it even if its name appears read-like.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add configured-runtime MCP tests that initially fail for API-key-capable, OAuth-required, and unavailable-capability outcomes across every public tool family; add failures for missing configuration returning representative data, unobserved live request construction, incomplete family coverage, absent opt-in authorization, unsafe tool selection, and secret exposure.
- **Green**: Add only the capability matrix, controlled request observation, safe MCP error classification, live-smoke selection rules, and credential-redacted reporting required for those tests to pass. The configured-runtime suite must not make network requests.
- **Refactor**: Consolidate repeated capability classifications and reporting assertions while retaining separate per-tool-family outcomes. Run focused catalog and configured-runtime suites, then the full repository suite after focused tests pass.
- **Required test levels**: Deterministic configured-runtime integration tests through MCP for every public tool family; contract tests for capability classification, coverage, and safe errors; deterministic tests for opt-in gating, read-only allowlisting, timeout handling, and redaction; manually triggered live smoke verification only when authorized.
- **Documentation and docstrings**: Every new or changed Python function in scope must have a reStructuredText docstring that describes its purpose, arguments, return value, side effects, and credential-safe error behavior. Project documentation must distinguish `make test-tools`, configured-runtime verification, and the opt-in read-only live smoke workflow.
- **Pull-request evidence**: Include passing focused catalog and configured-runtime suite results and a passing full repository suite result. Include deterministic evidence that no network request occurs in configured-runtime tests and that live-smoke gating, allowlisting, and redaction work. Do not include real credentials or live response bodies in review evidence.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a configured-runtime MCP verification matrix that covers every public tool family and reports a separately classified outcome for each case.
- **FR-002**: The matrix MUST classify each verified case as API-key executable, OAuth-required, or unavailable because required runtime capability is absent, using the tool's documented capability boundary.
- **FR-003**: The matrix MUST invoke configured cases through the public MCP request route and MUST verify that an API-key executable case reaches the live runtime boundary through controlled request observation without making an external network request.
- **FR-004**: When required configuration or authorization is absent, the system MUST return a safe, actionable MCP error and MUST NOT return representative fixture data as though it were a configured-runtime result.
- **FR-005**: The matrix MUST fail and identify every public tool family that lacks a configured-runtime capability case.
- **FR-006**: The configured-runtime suite MUST prevent external network access and MUST fail safely if a case attempts an unexpected request or exceeds the suite's documented request boundary.
- **FR-007**: The system MUST provide a separately invoked live smoke workflow that requires an explicit enablement flag and the credentials required for its approved tools; without either prerequisite, it MUST fail closed before making a live request.
- **FR-008**: The live smoke workflow MUST invoke only an explicitly maintained set of documented public, read-only tools using reviewed public reference inputs.
- **FR-009**: The live smoke workflow MUST exclude mutations, uploads, deletes, ratings, reports, moderation actions, and any other tool not explicitly approved for the workflow.
- **FR-010**: The live smoke workflow MUST report a separate outcome for every selected tool, apply bounded request counts and time limits, and distinguish successful structured results, documented safe availability errors, and actionable failures.
- **FR-011**: All configured-runtime and live-smoke output and persisted verification evidence MUST redact credentials, authorization material, secret-bearing inputs, request headers, and full upstream response bodies.
- **FR-012**: Project documentation MUST explain the distinct purpose and safe-use boundaries of `make test-tools`, configured-runtime verification, and the opt-in read-only live smoke workflow, including its credential, quota, and upstream-availability implications.
- **FR-013**: The opt-in live smoke workflow MUST remain excluded from ordinary pull-request checks, standard full-suite testing, and automated deployment gates.

### Key Entities

- **Capability Matrix Case**: A documented configured-runtime verification case for one public tool family, including its available credentials, expected capability classification, and expected safe outcome.
- **Capability Outcome**: The classified result of a matrix case: API-key executable, OAuth-required, or unavailable due to absent runtime capability.
- **Controlled Request Record**: Non-secret evidence that a configured MCP invocation attempted the expected live-runtime operation without sending it to the external service.
- **Live Smoke Allowlist Entry**: An explicitly approved public read-only tool and its reviewed public reference input for manual live verification.
- **Verification Report**: A credential-safe per-case or per-tool record of outcome, classification, and actionable failure context.

### Assumptions

- Existing tool metadata identifies the public tool families, their capability boundaries, and the corresponding upstream operations needed to construct a controlled live-runtime request.
- The project has a documented way to supply API-key and OAuth credentials without committing them to source control or test evidence.
- The live smoke workflow uses only public reference inputs and is manually run by an authorized operator after considering quota and upstream availability.

### Scope Boundaries

- This feature verifies configured runtime behavior; it does not add, remove, or change client-facing YouTube operations.
- Deterministic configured-runtime verification observes request construction and must not contact the external YouTube service.
- The live smoke workflow is deliberately read-only and opt-in; it is not a general end-to-end test, a normal continuous-integration check, or a deployment gate.
- Remote MCP endpoint verification is outside this feature and is addressed by OPS-405.

### Dependencies

- Shared authenticated live execution runtime from `YT-157`.
- Resource-family live-call retrofits from `YT-158`, `YT-159`, and `YT-160`.
- Deterministic public-route catalog coverage from `OPS-403`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A configured-runtime matrix run reports one classified outcome for 100% of public tool families in scope.
- **SC-002**: 100% of API-key-executable matrix cases demonstrate the expected live-runtime request construction without making an external network request.
- **SC-003**: 100% of matrix cases missing required configuration or authorization return the documented safe MCP error and return zero representative fixture results.
- **SC-004**: With the opt-in flag absent or required credentials missing, 100% of attempted live smoke runs make zero live requests and return a credential-safe prerequisite message.
- **SC-005**: In an authorized live smoke run, 100% of invoked tools are explicitly approved public read-only tools, with zero invocations of excluded mutation or sensitive operations.
- **SC-006**: 100% of configured-runtime and live-smoke reports redact credentials, authorization material, request headers, secret-bearing inputs, and full upstream response bodies.
- **SC-007**: Maintainers can distinguish and select the deterministic catalog, configured-runtime, and opt-in live smoke workflows from the project documentation on their first attempt.
