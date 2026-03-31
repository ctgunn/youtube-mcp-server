# Feature Specification: Terraform-Managed Hosted Networking for Durable Sessions

**Feature Branch**: `027-terraform-hosted-networking`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "Review the requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for FND-027, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Provision Hosted Networking with Infrastructure Code (Priority: P1)

An operator needs the hosted GCP environment to create the network resources required for durable Redis-backed MCP sessions as part of the reviewed infrastructure definition, so the platform can be stood up without manual VPC or connector setup.

**Why this priority**: This is the core value of FND-027. If the required hosted network path still depends on pre-existing manually created resources, durable hosted sessions remain fragile, hard to reproduce, and inconsistent with the project's Infrastructure as Code goal.

**Independent Test**: Can be fully tested by applying the supported GCP infrastructure definition in a clean environment and confirming that the required hosted network resources for durable session connectivity are created without separate manual networking steps.

**Acceptance Scenarios**:

1. **Given** a clean supported GCP environment for hosted deployment, **When** the operator applies the reviewed infrastructure definition, **Then** the required network resources for durable session connectivity are created as part of that apply path.
2. **Given** the hosted platform is configured for durable Redis-backed sessions, **When** the infrastructure definition is reviewed, **Then** the VPC, subnet, and Cloud Run connectivity path required for that session model are visible in version-controlled infrastructure artifacts.
3. **Given** a new environment is being prepared for the hosted MCP service, **When** the operator follows the documented provisioning path, **Then** they do not need a separate manual prerequisite workflow to create the supported network layer first.

---

### User Story 2 - Feed Hosted Networking Outputs into Deployment and Verification (Priority: P2)

An operator needs the infrastructure apply step to expose the network and connectivity values required by the hosted deployment and verification flow, so downstream rollout steps can use the managed networking path consistently.

**Why this priority**: Provisioning the network is not sufficient if deployment and verification still depend on hidden or manually copied values. The rollout path needs a clear handoff from infrastructure reconciliation to deployment and validation.

**Independent Test**: Can be fully tested by applying the infrastructure definition, exporting the resulting outputs, and confirming that the deployment and hosted verification workflow can identify the connectivity path without manual value reconstruction.

**Acceptance Scenarios**:

1. **Given** the infrastructure apply step has completed successfully, **When** deployment-ready outputs are exported, **Then** the hosted deployment workflow can identify the managed connectivity model and required network references from those outputs.
2. **Given** hosted verification is run after rollout, **When** the environment claims durable session support, **Then** the verification workflow can use the documented infrastructure outputs to validate the intended connectivity path.
3. **Given** a reviewer compares infrastructure outputs with deployment expectations, **When** they inspect the handoff artifacts, **Then** they can trace how hosted networking values move from infrastructure reconciliation into deployment and verification.

---

### User Story 3 - Remove Manual Networking Prerequisites from the GCP Runbook (Priority: P3)

An operator or maintainer needs the GCP runbook to describe one supported Terraform-managed networking path, so hosted deployment guidance no longer assumes manual creation of VPC, subnet, or Cloud Run connector resources outside the repository workflow.

**Why this priority**: Even if the infrastructure can provision the resources, the feature is incomplete if the documented operator workflow still treats networking as an external prerequisite. The runbook must match the supported managed path.

**Independent Test**: Can be fully tested by reviewing the operator documentation and confirming that the supported GCP deployment path no longer instructs the operator to pre-create networking resources manually for durable session support.

**Acceptance Scenarios**:

1. **Given** an operator reads the supported GCP runbook, **When** they prepare a hosted deployment for durable sessions, **Then** the documented prerequisites exclude manual creation of the supported VPC, subnet, and Cloud Run connectivity resources.
2. **Given** a maintainer reviews the hosted deployment documentation, **When** they compare the runbook with the infrastructure definition, **Then** both describe the same Terraform-managed networking path.
3. **Given** a deployment fails because the managed network layer cannot be provisioned, **When** the operator reviews the runbook, **Then** they can identify the failure as a provisioning issue rather than an undocumented prerequisite they were expected to complete manually.

### Edge Cases

- What happens when Terraform is applied in an environment where similarly named network resources already exist outside the supported managed path?
- What happens when durable session support is enabled but the network connectivity path cannot be provisioned in the selected region or project?
- How does the deployment handoff behave when infrastructure outputs exist but the connectivity model is incomplete or inconsistent with the hosted session configuration?
- What happens when an operator attempts to use the hosted deployment workflow before the Terraform-managed network layer has been applied successfully?
- How is the supported GCP path documented when local development and hosted-like local verification do not require the cloud network layer at all?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing contract, infrastructure, and documentation checks proving the supported GCP path still depends on manually supplied networking resources, does not export required connectivity outputs, or leaves deployment and verification unable to identify the managed network path.
- **Green**: Introduce the smallest infrastructure, output, deployment-handoff, and documentation changes required for the supported GCP durable-session path to provision its networking layer through Terraform and expose that path clearly to rollout and verification.
- **Refactor**: Consolidate duplicated networking assumptions across infrastructure variables, outputs, deployment guidance, and verification guidance; remove stale references to manual prerequisites; and rerun the full repository verification suite after the feature passes.
- Required test levels: unit checks for infrastructure-output normalization where applicable; contract tests for deployment-handoff and runbook expectations; integration tests for Terraform-managed networking inputs and outputs; end-to-end hosted verification covering durable-session connectivity after the managed network layer is applied.
- Pull request evidence must include failing-to-passing coverage for missing networking-output handoff, one reviewed Terraform plan or equivalent verification artifact showing managed network resources in scope, updated GCP operator documentation, and a passing full-suite run using `pytest` and `ruff check .`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The supported GCP hosted deployment path MUST provision the network resources required for durable hosted session connectivity through version-controlled Terraform definitions.
- **FR-002**: The supported GCP hosted deployment path MUST provision the VPC network required for the durable session connectivity model rather than assuming that network already exists as a manual prerequisite.
- **FR-003**: The supported GCP hosted deployment path MUST provision the subnet resources required for the durable session connectivity model rather than assuming that subnets already exist as a manual prerequisite.
- **FR-004**: The supported GCP hosted deployment path MUST provision the Cloud Run connectivity resource required for the durable session backend path when that connectivity resource is part of the selected session model.
- **FR-005**: The infrastructure definition MUST express the relationship between the hosted runtime network path and the durable session backend network path clearly enough that reviewers can determine how Cloud Run reaches the shared session backend.
- **FR-006**: Terraform outputs MUST expose the hosted networking and connectivity values that the deployment and hosted verification workflow require for the supported GCP path.
- **FR-007**: Deployment and hosted verification guidance MUST consume or reference the Terraform-managed networking outputs rather than instructing operators to discover or reconstruct those values manually.
- **FR-008**: The supported GCP runbook MUST document one operator workflow in which the managed network layer is provisioned through Terraform before application rollout.
- **FR-009**: The supported GCP runbook MUST no longer describe pre-existing manually created VPC, subnet, or Cloud Run connectivity resources as required prerequisites for durable hosted session support.
- **FR-010**: The infrastructure and documentation for this feature MUST preserve a clear boundary between the minimal local runtime path and the hosted GCP networking path so local development does not appear to require cloud network provisioning.
- **FR-011**: If durable hosted session support is enabled for a hosted environment, the deployment readiness and verification workflow MUST treat missing or incomplete managed network provisioning as a release-blocking condition.
- **FR-012**: The feature MUST keep hosted deployment reviewable by making the managed network layer visible in normal Terraform plans, outputs, and operator documentation.
- **FR-013**: The supported GCP path MUST preserve the existing application-layer authentication contract and hosted MCP behavior while replacing manual network prerequisites with Terraform-managed equivalents.
- **FR-014**: Operator guidance MUST identify the expected failure signals and remediation path when the managed network layer cannot be provisioned or does not match the durable session connectivity model.

### Key Entities *(include if feature involves data)*

- **Hosted Network Layer**: The provider-specific set of network resources that enables the hosted runtime to reach the durable session backend in the supported GCP environment.
- **Connectivity Resource**: The hosted runtime attachment point used to route Cloud Run traffic to the durable session backend network path when the selected session model requires it.
- **Networking Output Set**: The deployment-ready values emitted after infrastructure reconciliation that describe the managed network path and are consumed by rollout and verification workflows.
- **Durable Session Connectivity Model**: The documented operator-facing description of how the hosted runtime reaches the shared session backend needed for MCP session continuity.
- **Operator Runbook**: The reviewed guidance that explains how to provision, deploy, verify, and troubleshoot the supported GCP hosted networking path.

### Assumptions

- FND-022 established the need for provider-specific secret and durable-session wiring, but the supported GCP path still treats some hosted networking resources as external inputs rather than Terraform-managed resources.
- FND-025 established the checked-in deployment orchestration path, and FND-027 extends the infrastructure side of that path rather than redesigning pipeline behavior.
- The supported hosted durable-session backend remains Redis-backed for the GCP path covered by this feature.
- This feature covers the supported GCP provider path only; broader multi-provider networking patterns remain governed by the shared infrastructure strategy from earlier features.

### Dependencies

- `FND-022` Hosted dependency wiring for secrets and durable sessions
- `FND-025` Automated hosted deployment orchestration

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In release verification, 100% of supported GCP hosted environments claiming durable session support can provision the required network layer through Terraform without separate manual creation of VPC, subnet, or Cloud Run connectivity resources.
- **SC-002**: In release verification, 100% of successful infrastructure applies for the supported GCP durable-session path emit the networking outputs required by deployment and hosted verification.
- **SC-003**: In deployment-readiness testing, 100% of scenarios with missing or incomplete managed network provisioning fail before the hosted rollout is reported as ready for durable session support.
- **SC-004**: A maintainer can inspect the reviewed infrastructure definition and identify the hosted network path for durable sessions in 15 minutes or less.
- **SC-005**: A first-time operator can follow the supported GCP runbook and provision the managed hosted networking path for durable sessions in 30 minutes or less, excluding external approval wait times and provider provisioning latency.
- **SC-006**: The supported GCP runbook contains zero instructions that require manual pre-creation of the VPC, subnet, or Cloud Run connectivity resources used by the documented durable-session path.
