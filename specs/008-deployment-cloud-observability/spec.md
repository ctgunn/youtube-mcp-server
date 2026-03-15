# Feature Specification: FND-008 Deployment Execution + Cloud Run Observability

**Feature Branch**: `008-deployment-cloud-observability`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "I need you to read requirements/PRD.md to get an overview of the project. Then, I need you to work on the requirements for FND-008 as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute a Hosted Deployment in One Workflow (Priority: P1)

As an operator, I can run one deployment workflow that actually creates a new hosted service revision so I do not need to translate a rendered command into separate manual steps.

**Why this priority**: FND-006 established the required deployment inputs and verification expectations, but FND-008 is only complete when operators can execute the deployment directly and treat the workflow as the source of truth.

**Independent Test**: Can be fully tested by starting with a valid deployment target, running the documented deployment workflow once, and confirming that a new hosted revision is created without requiring manual reconstruction of the deploy command.

**Acceptance Scenarios**:

1. **Given** all required deployment inputs are available, **When** an operator runs the deployment workflow, **Then** the workflow performs the hosted deployment and reports that a new revision was created.
2. **Given** the deployment target rejects the deployment or required inputs are invalid, **When** the operator runs the deployment workflow, **Then** the workflow stops with actionable failure output and does not report the deployment as successful.
3. **Given** a deployment succeeds, **When** the operator reviews the workflow result, **Then** the result identifies the created revision and the hosted service endpoint that should be used for verification.

---

### User Story 2 - Capture Revision Metadata for Verification and Audit (Priority: P1)

As an operator, I can review a deployment record that captures the created revision, service URL, and runtime settings so I can verify what was deployed without re-querying the platform manually.

**Why this priority**: A successful deploy is not operationally useful if the team cannot prove which revision was created or which runtime settings were applied.

**Independent Test**: Can be fully tested by completing one deployment and checking that the produced deployment record includes revision identity, service endpoint, and the runtime settings required by the project’s hosted baseline.

**Acceptance Scenarios**:

1. **Given** a deployment completes successfully, **When** the operator inspects the deployment record, **Then** it includes the revision name and hosted service URL for the new revision.
2. **Given** a deployment completes successfully, **When** the operator inspects the deployment record, **Then** it includes the runtime identity, scaling bounds, concurrency, timeout, and environment profile used for that revision.
3. **Given** deployment metadata cannot be fully captured after the platform reports success, **When** the workflow finishes, **Then** the workflow marks the deployment result as incomplete and identifies the missing metadata.

---

### User Story 3 - Inspect Hosted Runtime Logs for Request Diagnostics (Priority: P2)

As an operator, I can inspect structured hosted request logs in the platform logging system so I can trace requests by request ID, path, status, and tool name where applicable.

**Why this priority**: Operators need usable runtime diagnostics once the hosted service is live, but deployment execution and metadata capture are slightly higher priority because they gate every later environment verification step.

**Independent Test**: Can be fully tested by sending hosted health, readiness, and MCP requests after deployment and confirming that each request produces a structured log record with the required diagnostic fields.

**Acceptance Scenarios**:

1. **Given** a hosted request reaches the service, **When** the request completes, **Then** a structured log record is emitted with request ID, request path, outcome status, and timestamp.
2. **Given** a hosted MCP tool invocation completes, **When** the operator inspects the corresponding request log, **Then** the log record includes the invoked tool name in addition to the common request fields.
3. **Given** a hosted request fails because of an invalid path, invalid request, or tool error, **When** the operator inspects logs, **Then** the failed request still has a structured log record that can be correlated by request ID and status.

### Edge Cases

- What happens when the hosted platform creates a revision but the workflow cannot retrieve one or more metadata fields needed for the deployment record?
- How does the workflow report partial success when deployment completes but post-deployment verification cannot begin because the hosted URL is missing or malformed?
- How are non-tool hosted requests such as liveness and readiness checks logged when there is no tool name to record?
- What happens when a request fails before tool dispatch, such as an unsupported path or malformed MCP payload?
- How does the workflow distinguish a failed deployment from a successful deployment that produced a not-ready revision?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- Red:
  - Add failing tests proving the deployment workflow performs the hosted deployment action instead of only printing the command that would be run.
  - Add failing tests proving successful deployment output includes revision identity, service URL, and required runtime settings in one operator-visible record.
  - Add failing tests proving hosted request logs are emitted in structured form for successful requests, failed requests, probe requests, and tool calls.
- Green:
  - Implement the smallest deployment workflow change that executes the hosted deploy and returns a success or failure result with deployment metadata.
  - Add deployment result capture that records revision identity, hosted endpoint, and core runtime settings immediately after a successful deploy.
  - Ensure every hosted request path emits a structured log record with the required correlation and diagnostic fields.
- Refactor:
  - Consolidate deployment result formatting so deployment execution, verification, and operator evidence all read from one consistent deployment record.
  - Remove duplicate request-log shaping logic so success and failure paths emit the same core field set.
  - Tighten regression coverage so future deployment or logging changes cannot silently drop required metadata fields.
- Required test levels: unit, integration, contract, end-to-end.
- Pull request evidence expectations:
  - Passing automated tests for deployment execution behavior, deployment metadata capture, and structured hosted logging.
  - Captured evidence of one deployment run that includes the created revision, hosted URL, and runtime settings summary.
  - Captured hosted request log examples covering at least one probe request, one successful MCP request, and one failed hosted request.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide one operator-facing deployment workflow that performs the hosted service deployment rather than only rendering deployment instructions.
- **FR-002**: System MUST validate required deployment inputs before attempting deployment and MUST stop with actionable error guidance when required inputs are missing or invalid.
- **FR-003**: System MUST report whether the hosted deployment created a new revision, failed before revision creation, or completed with incomplete metadata capture.
- **FR-004**: System MUST capture the created revision name for every successful hosted deployment.
- **FR-005**: System MUST capture the hosted service URL associated with the deployed revision for every successful hosted deployment.
- **FR-006**: System MUST capture the core runtime settings used for the deployed revision, including runtime identity, environment profile, scaling bounds, concurrency, and request timeout.
- **FR-007**: System MUST present deployment output in a form that operators can retain as evidence for verification and audit without manually reconstructing the deployment context.
- **FR-008**: System MUST identify when a deployment succeeded at the platform level but the deployment record is missing required metadata, and MUST surface that condition as an incomplete outcome rather than a clean success.
- **FR-009**: System MUST emit a structured runtime log record for every hosted request handled by the service, including successful and failed requests.
- **FR-010**: System MUST include request ID, request path, outcome status, severity, timestamp, and request latency in each hosted request log record.
- **FR-011**: System MUST include tool name in the hosted request log record when the request is a tool invocation and a tool name is available.
- **FR-012**: System MUST emit structured log records for hosted liveness, readiness, MCP, and unsupported-path requests so operators can diagnose both expected and unexpected traffic patterns.
- **FR-013**: System MUST ensure hosted request logs are emitted through the service runtime output in a format that the platform logging system can ingest without custom operator parsing.
- **FR-014**: System MUST let operators correlate a failed hosted response with its corresponding log record using the request ID returned by the service or generated during request handling.
- **FR-015**: System MUST document how operators use the deployment result and hosted logs together to verify a revision and diagnose failures after deployment.

### Key Entities *(include if feature involves data)*

- **Deployment Run Record**: The operator-visible record produced by one deployment attempt, including outcome, revision identity, hosted endpoint, runtime settings, and execution timestamp.
- **Hosted Revision Metadata**: The subset of deployment facts required to identify and verify a newly created hosted revision.
- **Hosted Request Log Event**: One structured runtime log record describing a handled hosted request, including request identifiers, path, status, latency, and optional tool name.
- **Deployment Outcome State**: The deployment status classification used by operators to distinguish success, failure, and incomplete metadata capture.

### Dependencies

- FND-005 must already provide request context, normalized logging fields, and error handling behavior that this feature can extend to hosted runtime output.
- FND-006 must already define the deployment inputs, hosted verification expectations, and baseline hosted runtime settings for the foundation service.
- FND-007 must already define the final hosted route semantics so the emitted request logs reflect the correct hosted paths and outcome statuses.
- A hosted deployment target and operator access to the platform logging system must exist before this workflow can be proven end to end.

### Assumptions

- The deployment workflow remains focused on creating one hosted revision per run rather than coordinating multi-step rollout strategies.
- Operators need deployment evidence immediately from the workflow output and do not want to assemble it manually from multiple platform queries.
- Hosted runtime logs are expected for both operator probe traffic and MCP client traffic because both are needed during rollout and incident diagnosis.
- The existing request ID model remains the primary correlation mechanism between hosted responses and runtime logs.
- This feature covers deployment execution and baseline runtime observability only; alerting and broader production hardening remain outside this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful operator deployment runs produce a deployment record that includes revision name, hosted service URL, and the required runtime settings summary.
- **SC-002**: At least 95% of deployment failures identify the failing stage and required corrective action within 5 minutes using only the workflow output and operator documentation.
- **SC-003**: 100% of hosted probe and MCP requests exercised during deployment verification produce a structured log record with request ID, path, status, and latency.
- **SC-004**: 100% of hosted MCP tool invocation logs exercised during verification include the invoked tool name when the request reaches tool dispatch.
- **SC-005**: Operators can complete deployment execution and collect the corresponding deployment record and initial hosted log evidence in 15 minutes or less, excluding external platform queue time.
