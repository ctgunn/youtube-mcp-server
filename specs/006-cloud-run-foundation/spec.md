# Feature Specification: FND-006 Cloud Run Foundation Deployment

**Feature Branch**: `006-cloud-run-foundation`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: User description: "Read requirements/PRD.md to get an overview of the project. Then begin working on the requirements for FND-006 as outlined in requirements/spec-kit-seed.md?"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy a Reproducible Service Revision (Priority: P1)

As an operator, I can deploy the foundation server to the hosted runtime using a repeatable process so the service can be brought up consistently in a new environment.

**Why this priority**: The project cannot progress to YouTube tool delivery until the baseline server can be deployed reliably outside local development.

**Independent Test**: Can be fully tested by executing the documented deployment process in a clean environment and confirming a new service revision becomes available with the expected runtime settings.

**Acceptance Scenarios**:

1. **Given** a deployment target with the required configuration and secrets available, **When** an operator runs the documented deployment process, **Then** a new service revision is created successfully.
2. **Given** a successful deployment, **When** the operator reviews the deployed revision, **Then** the revision shows the required runtime identity, scaling bounds, request concurrency, timeout, and configuration inputs.
3. **Given** required deployment inputs are missing or invalid, **When** the operator attempts deployment, **Then** the process fails with actionable guidance and does not present the revision as ready for traffic.

---

### User Story 2 - Verify Operational Readiness After Deployment (Priority: P1)

As an operator, I can confirm health and readiness on the deployed endpoint so I know whether the service is safe to expose to MCP clients.

**Why this priority**: A deployment that cannot prove liveness and readiness is not production-usable and should not be treated as complete.

**Independent Test**: Can be fully tested by calling the deployed health and readiness endpoints after deployment and confirming both success and failure-path behavior.

**Acceptance Scenarios**:

1. **Given** a newly deployed revision with valid startup configuration, **When** an operator calls the deployed liveness endpoint, **Then** the service reports a healthy liveness state.
2. **Given** a newly deployed revision with valid startup configuration, **When** an operator calls the deployed readiness endpoint, **Then** the service reports ready status and passing checks.
3. **Given** a deployed revision with invalid or incomplete runtime configuration, **When** an operator calls the readiness endpoint, **Then** the service reports not-ready status with a machine-readable reason.

---

### User Story 3 - Prove End-to-End MCP Baseline Behavior (Priority: P2)

As an MCP client integrator, I can initialize against the deployed service, discover tools, and invoke a baseline tool so I know the hosted endpoint supports the minimum MCP round-trip.

**Why this priority**: The business value of this slice is not just deployment; it is proof that the deployed service can actually serve MCP traffic successfully.

**Independent Test**: Can be fully tested by performing initialize, list tools, and baseline tool invocation against the deployed endpoint and validating stable responses.

**Acceptance Scenarios**:

1. **Given** a deployed revision that is reporting ready, **When** an MCP client sends an initialize request, **Then** the service returns declared capabilities without transport-level failure.
2. **Given** a deployed revision that is reporting ready, **When** an MCP client requests the available tools, **Then** the service returns the baseline tool set with names and descriptions.
3. **Given** a deployed revision that is reporting ready, **When** an MCP client invokes a baseline tool, **Then** the service returns a successful structured response from the hosted endpoint.

### Edge Cases

- What happens when deployment completes but startup validation keeps the revision in a not-ready state?
- How does the workflow behave when health checks pass but MCP initialize or baseline tool invocation fails?
- How is deployment verification handled when the revision is reachable but required runtime metadata does not match the documented configuration?
- What evidence is retained when deployment succeeds but post-deploy verification only partially passes?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- Red:
  - Add failing validation for the deployment documentation and release checklist to prove required deployment inputs, expected runtime settings, and post-deploy verification steps are all defined.
  - Add failing integration or environment-verification tests for hosted liveness, readiness, initialize, list-tools, and baseline tool invocation paths.
  - Add failing checks for deployment result capture so revision identity, deployed endpoint, and verification evidence must be recorded.
- Green:
  - Define the repeatable deployment workflow and required operator inputs.
  - Implement the deployment configuration needed to produce a hosted revision that can pass health and MCP verification.
  - Add post-deploy verification steps and evidence capture for health, readiness, and MCP baseline round-trip.
- Refactor:
  - Consolidate duplicated deployment variables and verification steps into a single maintained source of truth.
  - Tighten regression coverage so changes to deployment settings or baseline tools cannot silently break hosted verification.
  - Simplify operator steps without reducing the evidence required to prove hosted readiness.
- Required test levels: unit, integration, contract, end-to-end.
- Pull request evidence expectations:
  - Passing automated checks covering deployment configuration validation and hosted verification helpers.
  - Captured evidence of a successful deployment revision.
  - Captured results for deployed liveness, readiness, initialize, list-tools, and baseline tool invocation flows.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a documented, repeatable deployment workflow that produces a new hosted foundation-service revision from the current codebase.
- **FR-002**: System MUST define the full set of required deployment inputs, including environment-specific configuration values, secret references, runtime identity, scaling bounds, request concurrency, and timeout settings.
- **FR-003**: System MUST prevent a deployment from being treated as complete until required deployment inputs have been supplied and validated.
- **FR-004**: System MUST expose the deployed service at a stable endpoint that operators can use for health and MCP verification.
- **FR-005**: System MUST allow operators to confirm that the deployed revision reports healthy liveness status.
- **FR-006**: System MUST allow operators to confirm that the deployed revision reports ready status only when startup validation has passed.
- **FR-007**: System MUST return a structured not-ready response when required runtime configuration is missing or invalid after deployment.
- **FR-008**: System MUST allow an MCP client to complete initialize against the deployed endpoint and receive declared server capabilities.
- **FR-009**: System MUST allow an MCP client to list the deployed baseline tools and receive the currently registered baseline tool names and descriptions.
- **FR-010**: System MUST allow an MCP client to invoke at least one baseline tool successfully against the deployed endpoint.
- **FR-011**: System MUST produce deployment verification evidence that records the deployed revision identity, endpoint under test, verification timestamp, and pass/fail result for each required post-deploy check.
- **FR-012**: System MUST define operator-facing failure guidance for deployment failures, not-ready revisions, and unsuccessful MCP verification so remediation can begin without source-code inspection.

### Key Entities *(include if feature involves data)*

- **Deployment Input Set**: The complete collection of operator-supplied values and references required to create a hosted revision safely and consistently.
- **Hosted Revision Record**: The identity and configuration summary of the deployed service revision being verified.
- **Verification Check Result**: The outcome of one post-deploy validation step, including the check performed, timestamp, target endpoint, and result status.
- **Baseline MCP Session**: The minimum hosted client interaction used to prove initialize, tool discovery, and baseline tool invocation against the deployed service.

### Dependencies

- FND-003 baseline server tools must already be available for hosted MCP verification.
- FND-004 configuration and startup validation behavior must be complete so readiness reflects real deployment state.
- FND-005 health endpoints, structured errors, logging, and metrics must already exist for hosted verification and operational support.
- A target hosted environment, deployment identity, and required secret/configuration sources must be provisioned before deployment begins.

### Assumptions

- The first delivery target is a single reproducible hosted revision rather than a multi-region or blue/green rollout.
- Baseline MCP verification is satisfied by initialize, tool discovery, and one successful baseline tool invocation.
- Operators need written deployment and verification steps that can be executed in a clean environment without relying on local tribal knowledge.
- Deployment evidence can be stored alongside normal delivery artifacts and does not require a separate approval system for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A clean-environment operator can complete the documented deployment workflow and produce a new hosted revision in 15 minutes or less, excluding external platform queue time.
- **SC-002**: 100% of completed foundation deployments include recorded pass/fail results for liveness, readiness, initialize, tool discovery, and baseline tool invocation checks.
- **SC-003**: 100% of successful hosted revisions pass both liveness and readiness verification before being declared ready for MCP client use.
- **SC-004**: At least 95% of hosted verification runs complete initialize, tool discovery, and baseline tool invocation successfully on the first attempt when required inputs are valid.
- **SC-005**: Operators can identify the specific failed stage of deployment or verification within 5 minutes using the recorded deployment evidence and operator-facing guidance.
