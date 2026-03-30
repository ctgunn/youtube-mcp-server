# Feature Specification: Automated Hosted Deployment Orchestration

**Feature Branch**: `025-hosted-deploy-orchestration`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "Read the requirements/PRD.md to get an overview of the project and its goals for context. The, work on the requirements for FND-025, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy the Hosted Platform from a Branch Push (Priority: P1)

An operator needs a branch push to trigger one checked-in deployment workflow that reconciles the hosted platform, rolls out the current application revision, and verifies that the hosted MCP endpoint still works before the rollout is considered successful.

**Why this priority**: This is the core promise of FND-025. Without a reliable push-triggered deployment path, hosted delivery still depends on manual operator steps and can drift away from the versioned application and infrastructure definitions.

**Independent Test**: Can be fully tested by pushing a qualifying change to the deployment branch and confirming one automated workflow runs from repository-defined automation, completes the hosted rollout, and blocks completion when hosted verification fails.

**Acceptance Scenarios**:

1. **Given** the hosted platform definitions and application changes are committed to the deployment branch, **When** the qualifying branch push occurs, **Then** one checked-in deployment workflow runs the full hosted rollout path for that revision.
2. **Given** the automated rollout completes the infrastructure and application update steps, **When** hosted verification succeeds, **Then** the deployment is recorded as successful for that pushed revision.
3. **Given** the automated rollout reaches hosted verification, **When** hosted verification fails, **Then** the deployment is marked failed and the workflow does not report a successful rollout.

---

### User Story 2 - Review and Trust Deployment Logic in Version Control (Priority: P2)

A maintainer needs the deployment automation to live in version control and follow the repository's published deployment path so infrastructure changes, rollout behavior, and hosted verification can be reviewed and evolved together.

**Why this priority**: The deployment path becomes hard to audit if it bypasses repository logic or depends on hidden console-only steps. Keeping the orchestration checked in makes changes reviewable and reduces operational surprises.

**Independent Test**: Can be fully tested by inspecting the checked-in automation definition for a deployment revision and confirming it uses the repository's documented deployment path, consumes repository-produced infrastructure outputs, and does not reduce deployment to an image-only update.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the automated deployment definition, **When** they inspect the rollout steps, **Then** they can trace infrastructure reconciliation, application rollout, and hosted verification through version-controlled automation.
2. **Given** a deployment revision requires both infrastructure and application changes, **When** the workflow runs, **Then** it uses the repository's deployment path rather than bypassing it with a direct image-only update.
3. **Given** infrastructure reconciliation produces deployment inputs for the hosted runtime, **When** the application rollout step starts, **Then** it uses those outputs to complete the hosted deployment path.

---

### User Story 3 - Distinguish Automation from Secret Value Management (Priority: P3)

An operator needs the automated workflow to set up required secret references and deployment wiring while making it explicit which secret values must still be populated or rotated through a separate operator-managed process.

**Why this priority**: Deployment automation is only trustworthy if operators understand the boundary between infrastructure-managed secret references and the secret material that should remain under controlled operational ownership.

**Independent Test**: Can be fully tested by reviewing the deployment documentation and workflow outcomes to confirm that missing or unpopulated secret values are surfaced clearly and that automation does not imply secret contents are automatically created or rotated.

**Acceptance Scenarios**:

1. **Given** a first-time operator prepares the hosted deployment workflow, **When** they review the bootstrap guidance, **Then** they can identify which one-time prerequisites must be completed before push-triggered deployment can succeed.
2. **Given** the deployment workflow depends on required secret-backed inputs, **When** a referenced secret value has not been populated, **Then** the workflow fails with a clear outcome showing the rollout is not ready to proceed.
3. **Given** an operator reviews the automation boundary for secrets, **When** they inspect the documentation, **Then** it clearly distinguishes secret resource wiring from secret value population and ongoing secret administration.

### Edge Cases

- What happens when a qualifying branch push includes infrastructure changes but no application changes?
- What happens when a qualifying branch push includes application changes but no infrastructure drift is detected?
- How does the workflow behave when hosted verification fails after the new revision has been rolled out?
- How does the workflow surface missing bootstrap prerequisites so operators can correct them without guessing?
- What happens when a required secret reference exists but its value is missing, expired, or inaccessible at deployment time?
- How does the workflow avoid reporting success when one stage completes but a later verification stage fails?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing workflow, integration, and verification coverage for qualifying branch pushes, infrastructure reconciliation handoff, application rollout handoff, hosted verification failure handling, and missing bootstrap prerequisite scenarios.
- **Green**: Implement the smallest checked-in automation changes required so a qualifying branch push runs the full hosted deployment path, consumes infrastructure reconciliation outputs, uses the repository deployment path, and blocks success when hosted verification fails.
- **Refactor**: Consolidate duplicated deployment orchestration rules, align workflow and operator documentation to the same deployment path, and run the full repository verification flow after the feature passes.
- Required test levels: unit coverage for workflow decision points and outcome mapping; integration coverage for deployment-stage handoff and failure propagation; end-to-end or hosted verification coverage for a qualifying branch push through hosted endpoint validation.
- Pull request evidence must include one failing-to-passing workflow proof for hosted verification failure handling, one passing deployment run from a qualifying branch push, updated operator documentation for bootstrap prerequisites, and a passing full-suite run using `pytest` and `ruff check .`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide one checked-in automated deployment workflow for the intended deployment branch.
- **FR-002**: A qualifying push to the intended deployment branch MUST trigger the automated deployment workflow for the pushed revision.
- **FR-003**: The automated deployment workflow MUST reconcile hosted platform dependencies before completing application rollout.
- **FR-004**: The automated deployment workflow MUST deploy the current application revision through the repository's established deployment path rather than reducing deployment to an image-only runtime update.
- **FR-005**: The application rollout stage MUST consume the deployment inputs produced by the infrastructure reconciliation stage.
- **FR-006**: The automated deployment workflow MUST execute hosted verification after rollout and MUST treat hosted verification as a required release gate.
- **FR-007**: The automated deployment workflow MUST report the deployment as failed when hosted verification fails.
- **FR-008**: The automated deployment workflow MUST make test, build, rollout, and hosted verification stages observable in workflow results so operators can identify which stage failed.
- **FR-009**: The feature MUST document the one-time bootstrap prerequisites that must be completed before push-triggered deployment can run successfully.
- **FR-010**: The feature MUST distinguish infrastructure-managed secret reference wiring from operator-managed secret value population and ongoing secret administration.
- **FR-011**: If required secret-backed deployment inputs are missing, inaccessible, or unpopulated, the workflow MUST fail with a clear outcome that indicates deployment cannot proceed safely.
- **FR-012**: The automated deployment workflow MUST remain reviewable and maintainable through version-controlled definitions that evolve alongside application and infrastructure changes.
- **FR-013**: The feature MUST preserve a supported local development and verification path without requiring a qualifying branch push to validate ordinary application changes.

### Key Entities *(include if feature involves data)*

- **Deployment Branch**: The repository branch whose qualifying pushes trigger automated hosted deployment.
- **Deployment Workflow Run**: One end-to-end execution of the automated deployment process for a specific revision.
- **Infrastructure Reconciliation Output**: The deployment-ready values produced after hosted platform dependencies are reconciled and made available to later deployment stages.
- **Hosted Verification Result**: The pass or fail outcome proving whether the hosted MCP endpoint behaves correctly after rollout.
- **Bootstrap Prerequisite**: A one-time setup item that must be completed before push-triggered deployment can operate reliably.
- **Secret Wiring Boundary**: The documented separation between preparing secret references in deployment automation and populating or rotating secret values through operator-controlled processes.

### Assumptions

- Earlier infrastructure features already define the hosted platform resources, public reachability model, durable-session connectivity, and initialize-session correctness that this feature must automate rather than redesign.
- The repository already has an established application deployment path that this feature must orchestrate instead of replacing with an ad hoc rollout path.
- Hosted verification for the MCP endpoint already exists or can be invoked as a repository-supported verification step.
- The intended deployment branch is a single controlled branch used for hosted rollout automation rather than every development branch.
- Secret values remain operator-managed and are not auto-generated or auto-rotated by this feature.

### Dependencies

- `FND-019` Infrastructure as Code foundation
- `FND-021` Cloud Run public reachability for remote MCP
- `FND-022` Hosted dependency wiring for secrets and durable sessions
- `FND-024` Initialize handshake and session creation correctness

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In release verification, 100% of qualifying pushes to the intended deployment branch trigger exactly one automated deployment workflow run for the pushed revision.
- **SC-002**: In release verification, 100% of successful automated deployment runs complete infrastructure reconciliation, application rollout, and hosted verification without requiring undocumented manual intervention.
- **SC-003**: In release verification, 100% of hosted verification failures cause the automated deployment run to be marked failed rather than successful.
- **SC-004**: A maintainer can review the checked-in deployment workflow and identify the ordered rollout stages, stage inputs, and failure gate behavior in under 15 minutes.
- **SC-005**: A first-time operator can follow the documented bootstrap prerequisites and prepare the repository for push-triggered deployment in under 30 minutes, excluding external approval wait times.
- **SC-006**: In deployment-readiness testing, 100% of scenarios with missing or unpopulated required secret-backed inputs fail with a clear operator-facing outcome before the deployment is reported as successful.
