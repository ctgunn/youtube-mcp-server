# Feature Specification: Cloud Run Public Reachability for Remote MCP

**Feature Branch**: `021-cloud-run-reachability`  
**Created**: 2026-03-23  
**Status**: Draft  
**Input**: User description: "Read requirements/PRD.md to get an overview of the project and its goals for context. Then work on the requirements for FND-021, ans outline in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reach the Hosted MCP Service from a Trusted Remote Consumer (Priority: P1)

A remote MCP consumer needs to connect to the hosted service over the public Internet so hosted tool discovery and invocation can work without private network access or operator-specific manual exceptions.

**Why this priority**: Public reachability for trusted remote consumers is the core purpose of FND-021. Without it, the hosted MCP service cannot serve the external clients the project is intended to support.

**Independent Test**: Can be fully tested by deploying the hosted service with the documented public-access configuration, connecting from an external network path, and confirming the service is reachable before any application-layer authentication decision is made.

**Acceptance Scenarios**:

1. **Given** a hosted MCP deployment intended for trusted remote consumers, **When** an external client connects to the service URL, **Then** the service is reachable through the public Internet using the documented operator workflow.
2. **Given** the service is publicly reachable, **When** a trusted remote consumer sends a valid MCP request with acceptable application credentials, **Then** the request reaches the MCP layer and receives a normal application response.
3. **Given** the service is publicly reachable, **When** a remote consumer sends a request without acceptable application credentials, **Then** the request is rejected by the MCP layer rather than by cloud-level reachability controls.

---

### User Story 2 - Configure Public Access Intentionally and Reproducibly (Priority: P2)

An operator needs a repeatable workflow for enabling the required public reachability so production access does not depend on default platform behavior, one-time console actions, or tribal knowledge.

**Why this priority**: Reachability is not reliable if it only exists by accident or manual setup. The operator path must be explicit and reviewable for the hosted deployment to remain reproducible.

**Independent Test**: Can be fully tested by starting from a deployment path that does not yet permit the required public access, following the documented workflow, and confirming that the hosted service becomes publicly reachable in a repeatable way.

**Acceptance Scenarios**:

1. **Given** an operator is preparing a hosted deployment, **When** they follow the documented deployment workflow, **Then** the workflow explicitly includes the public-invocation configuration required for remote MCP access.
2. **Given** a reviewer inspects the deployment documentation or release evidence, **When** they assess the hosted configuration, **Then** they can confirm public reachability was enabled intentionally rather than assumed from platform defaults.
3. **Given** an operator repeats the documented workflow for another environment, **When** they apply the same steps, **Then** the resulting service reachability matches the documented remote-access expectation.

---

### User Story 3 - Distinguish Reachability Failures from Authentication Failures (Priority: P3)

An operator or integrator needs to tell whether a failed remote call was blocked by cloud-level access settings or by MCP-layer authentication so incidents can be diagnosed quickly and the right control can be corrected.

**Why this priority**: Once the service is publicly reachable, the next operational need is clarity. If cloud access failures and application authentication failures look the same, operators cannot debug integration issues efficiently.

**Independent Test**: Can be fully tested by following a documented verification flow that triggers both a cloud-level denial and an MCP-layer denial, then confirming the two outcomes are distinguishable to the operator.

**Acceptance Scenarios**:

1. **Given** cloud-level public invocation is not enabled, **When** an operator runs the hosted verification workflow, **Then** the result clearly indicates a reachability or platform-access denial rather than an MCP authentication failure.
2. **Given** public invocation is enabled but application credentials are missing or invalid, **When** the same verification workflow is run, **Then** the result clearly indicates an MCP-layer authentication denial.
3. **Given** an operator reads the runbook for hosted verification, **When** they compare the failure examples, **Then** they can identify which remediation belongs to cloud reachability and which belongs to application authentication.

### Edge Cases

- What happens when the service is publicly reachable but the published URL is incorrect, stale, or points to an older revision?
- How does the operator workflow handle a deployment that is reachable publicly but still rejects all requests because the MCP authentication configuration is incomplete?
- What happens when public reachability is removed or misconfigured after a previously working remote integration has been onboarded?
- How are operators guided when one environment is intentionally private while another environment is intended for trusted public remote consumers?
- What happens when release evidence claims public reachability but does not include proof that cloud-level denial and MCP-layer denial can be distinguished?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing verification that shows the current hosted deployment path does not yet guarantee intentional public reachability, does not clearly separate cloud-level denial from MCP-layer denial, or lacks reproducible evidence for remote MCP access.
- **Green**: Introduce the minimum deployment workflow, runbook updates, and hosted verification evidence required to make the service publicly reachable for trusted remote consumers while preserving application-layer authentication at the MCP surface.
- **Refactor**: Remove ambiguous wording around public access versus authentication, consolidate operator guidance into one repeatable verification path, tighten release evidence expectations, and rerun the full repository verification suite to confirm no existing workflows regress.
- Required test levels: unit checks for any configuration or release-evidence validation added for public-access expectations; integration checks for deployment workflow outcomes and hosted verification behavior; contract-style verification for operator documentation and failure-mode distinction; end-to-end hosted verification from an external client path.
- Pull request evidence must include failing-to-passing hosted reachability verification, documented proof that cloud-level denial and MCP-layer denial are distinguishable, operator-facing workflow evidence for intentional public access, and a full-suite pass using `pytest` with an expected zero-failure result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The hosted deployment workflow MUST explicitly support the public-invocation model required for trusted remote MCP consumers.
- **FR-002**: Public reachability for the hosted MCP service MUST be enabled intentionally through a reviewable operator workflow rather than assumed from platform defaults alone.
- **FR-003**: The project MUST preserve MCP-layer authentication as a separate control from cloud-level public reachability.
- **FR-004**: Operator documentation MUST explain the difference between Cloud Run public reachability and MCP bearer-token authentication in plain language.
- **FR-005**: Hosted verification guidance MUST include a reproducible workflow for confirming that the service is publicly reachable from an external client path.
- **FR-006**: Hosted verification guidance MUST include a reproducible workflow for confirming that MCP-layer authentication still protects the publicly reachable service.
- **FR-007**: The project MUST provide operator-facing evidence that a cloud-level access denial can be distinguished from an MCP-layer authentication denial.
- **FR-008**: Release or deployment documentation MUST describe the expected failure signals for both cloud-level denial and MCP-layer denial.
- **FR-009**: The public-access workflow MUST be repeatable across supported hosted environments that are intended to serve trusted remote MCP consumers.
- **FR-010**: The operator workflow MUST identify when a hosted environment is intentionally not configured for public remote access.
- **FR-011**: Public reachability changes MUST be visible in normal review artifacts so operators can assess exposure intent before rollout.
- **FR-012**: Hosted deployment guidance MUST identify the service URL or equivalent connection point that trusted remote consumers are expected to use after rollout.
- **FR-013**: Verification evidence MUST confirm that remote consumers can reach the hosted service without requiring private network connectivity or operator-specific manual allowlisting.
- **FR-014**: The feature MUST not weaken or replace the existing MCP-layer authentication expectations established for hosted remote consumption.
- **FR-015**: The hosted runbook MUST describe the remediation path for failed public reachability separately from the remediation path for failed MCP authentication.
- **FR-016**: This feature MUST preserve the existing local-first development workflow and MUST NOT require public hosted infrastructure access for minimum local execution.

### Key Entities *(include if feature involves data)*

- **Public Reachability Workflow**: The documented operator path that enables and verifies public remote access to the hosted MCP service.
- **Remote Consumer Connection Point**: The published hosted service address that trusted external MCP consumers use to connect.
- **Cloud-Level Access State**: The hosted deployment state that determines whether the service can be reached publicly at all.
- **MCP Authentication State**: The application-layer access state that determines whether a publicly reachable request is authorized to use the MCP service.
- **Verification Evidence Set**: The reviewable proof that demonstrates public reachability, authentication enforcement, and distinguishable failure outcomes.

## Assumptions

- FND-006 established the baseline hosted deployment path and Cloud Run runtime for the MCP service.
- FND-013 established the requirement that hosted remote MCP access use application-layer authentication and transport hardening.
- FND-020 established that hosted platform capabilities should remain reviewable and reproducible even when provider-specific adapters are involved.
- Trusted remote MCP consumers are expected to connect over the public Internet, not through private network peering or one-off operator allowlists.
- Some hosted environments may remain intentionally private, but any environment claimed as supporting trusted remote MCP access must follow this feature's public-reachability workflow.

## Dependencies

- `FND-006` Cloud Run foundation deployment
- `FND-013` Remote MCP security and transport hardening
- `FND-020` Cloud-agnostic infrastructure module strategy

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator can follow the documented hosted workflow and enable public reachability for an intended remote-access environment in 20 minutes or less, excluding external approval wait times.
- **SC-002**: In release verification, 100% of environments claimed as supporting trusted remote MCP access include reviewable evidence of intentional public reachability.
- **SC-003**: In hosted verification, operators can distinguish cloud-level access denial from MCP-layer authentication denial on the first diagnostic attempt in at least 95% of test runs.
- **SC-004**: A trusted remote consumer can complete an initial connection attempt to the published hosted service address in 5 minutes or less using only the documented operator-provided connection details.
- **SC-005**: Documentation review confirms that 100% of public-access guidance for this feature explains the difference between public reachability and MCP authentication without contradictory instructions.
- **SC-006**: Minimum local execution remains unchanged, with developers able to complete the documented local setup in 15 minutes or less without enabling any public hosted endpoint.
