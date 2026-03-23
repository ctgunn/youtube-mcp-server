# Feature Specification: Infrastructure as Code Foundation

**Feature Branch**: `019-iac-foundation`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: User description: "Read the requirements/PRD.md to get an overview of the project and the goals of the project for context. Then, begin working on the requirements for FND-019, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Provision the Hosted Platform from Versioned Definitions (Priority: P1)

An operator needs to create the hosted MCP platform and its required dependencies from versioned infrastructure definitions so service setup does not rely on one-off console work or undocumented manual steps.

**Why this priority**: This is the core value of FND-019. If the hosted platform still depends on manual cloud setup, the foundation remains fragile, difficult to review, and hard to reproduce across environments.

**Independent Test**: Can be fully tested by starting from an environment without the hosted platform, running the documented provisioning workflow from versioned definitions, and confirming all required hosted resources become available without undocumented manual setup.

**Acceptance Scenarios**:

1. **Given** a target environment has no hosted MCP infrastructure provisioned, **When** the operator follows the documented infrastructure workflow, **Then** the required hosted platform resources are created from versioned definitions.
2. **Given** the hosted platform requires secrets, configuration entry points, and durable session support, **When** provisioning completes, **Then** those dependencies are represented by the infrastructure definitions and ready for application deployment.
3. **Given** a reviewer inspects the infrastructure change set, **When** they compare it with the hosted platform requirements, **Then** they can identify the required infrastructure from versioned code rather than from separate manual instructions.

---

### User Story 2 - Deploy the Application Through a Reproducible Hosted Path (Priority: P2)

A maintainer needs a documented deployment path that uses the provisioned infrastructure inputs consistently so application rollout is repeatable across supported environments and does not require editing application code for each environment.

**Why this priority**: Provisioning infrastructure alone is not enough. The hosted deployment path must remain reproducible and environment-aware, otherwise infrastructure and application rollout will drift apart.

**Independent Test**: Can be fully tested by provisioning one target environment, supplying only documented environment-specific inputs, running the documented deployment path, and confirming the hosted service can be deployed without modifying application source files.

**Acceptance Scenarios**:

1. **Given** the hosted infrastructure has been provisioned for an environment, **When** a maintainer supplies the documented environment-specific inputs, **Then** the service can be deployed through the documented hosted deployment path without changing application code.
2. **Given** multiple supported environments need different values, **When** maintainers prepare deployment inputs, **Then** the differences are handled through documented injectable inputs rather than environment-specific source changes.
3. **Given** a new maintainer reviews the deployment documentation, **When** they follow the hosted deployment path after infrastructure provisioning, **Then** they can complete the rollout without consulting undocumented console-only steps.

---

### User Story 3 - Preserve a First-Class Local Path While Documenting Hosted-Like Verification (Priority: P3)

A developer needs to keep the minimal local runtime path lightweight while still having a separate reproducible path for hosted-like verification when durable hosted dependencies must be exercised.

**Why this priority**: The PRD requires local execution to remain first-class. Infrastructure automation cannot turn cloud provisioning into a prerequisite for local development or basic verification.

**Independent Test**: Can be fully tested by following the documented minimal local run path without provisioning cloud infrastructure, then following the separate hosted-like verification path when durable hosted dependencies need to be exercised, and confirming the two paths are clearly distinguished.

**Acceptance Scenarios**:

1. **Given** a developer only needs the minimal local runtime, **When** they follow the local setup guidance, **Then** they can run and verify the service without provisioning hosted infrastructure first.
2. **Given** a developer or operator needs to verify behavior that depends on durable hosted dependencies, **When** they follow the hosted-like verification guidance, **Then** they can reproduce that dependency path separately from the minimal local run path.
3. **Given** a reader compares the local and hosted documentation, **When** they review setup prerequisites, **Then** it is clear which steps are required for minimal local development and which are only required for hosted or hosted-like verification.

### Edge Cases

- What happens when a required hosted dependency already exists with conflicting manual settings?
- How does the provisioning workflow behave when a required environment-specific input is missing or invalid?
- What happens when an operator can provision infrastructure but has not yet supplied the secrets or deployment inputs needed for the application rollout?
- How is the workflow documented when the minimal local runtime succeeds but hosted-like verification requires extra shared-state dependencies?
- What happens when a maintainer attempts to deploy the application to an environment that has not yet completed the required infrastructure provisioning step?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing tests and verification checks that prove required hosted infrastructure, environment-specific inputs, local-path separation, and hosted-like dependency reproduction are not yet fully represented by versioned definitions and operator documentation.
- **Green**: Introduce the minimum infrastructure definitions, environment-input documentation, and operator workflows required to provision the hosted platform, deploy the application reproducibly, and preserve a separate minimal local path.
- **Refactor**: Consolidate duplicated infrastructure assumptions across deployment and local-run documentation, remove remaining manual-only hosted setup steps for covered dependencies, and rerun the full repository verification suite to confirm the new foundation does not regress existing local or hosted workflows.
- Required test levels: unit checks for configuration and input-shape validation where applicable; integration checks for provisioning and deployment workflows; contract-style documentation verification for required infrastructure coverage and local-versus-hosted path separation; end-to-end operator verification for fresh-environment provisioning plus deployment.
- Pull request evidence must include failing-to-passing provisioning verification, a reproducible fresh-environment infrastructure run, a reproducible hosted deployment run, documentation proving local execution remains independent of cloud provisioning, and a full-suite pass using `pytest` with an expected zero-failure result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST define the required hosted MCP platform infrastructure in versioned Infrastructure as Code rather than relying on manual setup steps alone.
- **FR-002**: The Infrastructure as Code scope MUST cover the hosted application runtime resources required to run the MCP service in its supported hosted environment.
- **FR-003**: The Infrastructure as Code scope MUST cover the integration points required for runtime configuration and secret-backed values used by the hosted service.
- **FR-004**: The Infrastructure as Code scope MUST cover the durable hosted dependency requirements needed for reliable hosted MCP session behavior.
- **FR-005**: The project MUST provide one reproducible infrastructure provisioning path that an operator can execute from documented inputs and versioned definitions.
- **FR-006**: The project MUST provide one reproducible hosted application deployment path that uses the provisioned infrastructure and documented environment-specific inputs.
- **FR-007**: Environment-specific differences MUST be supplied through documented injectable inputs rather than through direct modification of application source code.
- **FR-008**: The infrastructure and deployment documentation MUST identify the required inputs, the expected outputs, and the order in which provisioning and deployment steps must occur.
- **FR-009**: The documentation MUST distinguish the minimum local runtime path from the full hosted-infrastructure provisioning path.
- **FR-010**: The minimum local runtime path MUST remain usable without provisioning cloud infrastructure as a prerequisite.
- **FR-011**: If hosted-like verification depends on durable shared-state services, the project MUST provide a separate reproducible path for that dependency setup.
- **FR-012**: The local-only path and the hosted-like verification path MUST identify their distinct prerequisites, intended use cases, and verification outcomes.
- **FR-013**: The versioned infrastructure definitions MUST be reviewable alongside application changes so maintainers can assess infrastructure impact in normal code review.
- **FR-014**: The provisioning and deployment workflows MUST fail with clear operator-facing guidance when required environment-specific inputs are missing.
- **FR-015**: Release evidence MUST prove that the covered hosted dependencies can be provisioned and the application can be deployed using the documented reproducible paths.
- **FR-016**: This feature MUST preserve the existing supported local development and verification workflow while adding the hosted infrastructure foundation.

### Key Entities *(include if feature involves data)*

- **Infrastructure Definition Set**: The versioned declarations that describe the hosted platform resources and dependency integration points required by the MCP service.
- **Environment Input Profile**: The documented set of environment-specific values an operator supplies to provision infrastructure and deploy the application without changing source code.
- **Hosted Dependency Set**: The required hosted resources beyond the application runtime itself, including configuration, secret integration points, and durable session support.
- **Provisioning Runbook**: The operator-facing instructions that explain how to create the hosted platform from versioned definitions, what inputs are required, and what outputs to expect.
- **Local Verification Path**: The documented workflow for running the service locally, separated into the minimum local runtime path and the hosted-like path used when durable shared-state behavior must be exercised.

## Assumptions

- FND-015 established that reliable hosted session continuity requires durable shared-state support for the supported deployment model.
- FND-016, FND-017, and FND-018 established the currently required hosted platform behavior and therefore define the dependencies that the infrastructure foundation must support.
- The primary goal of this feature is reproducibility and reviewability of hosted infrastructure, not expansion of the tool surface or changes to the local application behavior.
- A minimal local developer workflow must remain available even if a fuller hosted-like verification path needs additional dependencies.

## Dependencies

- `FND-015` Hosted MCP session durability
- `FND-016` Browser MCP CORS behavior
- `FND-017` Retrieval tool contract completeness
- `FND-018` JSON-RPC / MCP error code alignment

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In fresh-environment verification, 100% of hosted platform dependencies required by the current MCP foundation can be provisioned from versioned definitions without undocumented manual console steps.
- **SC-002**: An operator can complete the documented infrastructure provisioning path for one environment in 60 minutes or less, excluding external cloud approval wait times.
- **SC-003**: After infrastructure provisioning, a maintainer can complete the documented hosted application deployment path for one environment in 30 minutes or less without modifying application source code.
- **SC-004**: A developer can complete the documented minimum local runtime path in 15 minutes or less without provisioning cloud infrastructure.
- **SC-005**: When hosted-like verification requires durable shared-state support, a developer or operator can complete that separate dependency setup path in 20 minutes or less using only the documented workflow.
- **SC-006**: In release review, 100% of infrastructure-affecting changes for the covered hosted platform can be traced to versioned definitions and documented inputs in the same reviewable change set.
