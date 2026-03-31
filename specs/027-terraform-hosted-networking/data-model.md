# Data Model: Terraform-Managed Hosted Networking for Durable Sessions

## HostedNetworkingProfile

- **Purpose**: Represents one hosted GCP environment's operator-visible networking posture for durable Redis-backed sessions.
- **Fields**:
  - `environment`: hosted environment identifier such as `dev`, `staging`, or `prod`
  - `service_name`: hosted service identifier
  - `session_backend_type`: durable backend type for the environment
  - `connectivity_model`: operator-visible name of the hosted connectivity approach
  - `manual_prerequisites_removed`: whether the supported GCP path no longer depends on operator-created VPC, subnet, or connector resources
  - `status`: `draft`, `planned`, `provisioned`, `exported`, `verified`, or `failed`
- **Validation Rules**:
  - Durable hosted-session environments require `session_backend_type=redis`.
  - `connectivity_model` must describe a reviewable provider-specific network path.
  - `manual_prerequisites_removed=true` is required for environments claiming compliance with FND-027.
- **Relationships**:
  - Owns one `ManagedNetworkResourceSet`.
  - Owns one `CloudRunConnectivityPath`.
  - Produces one `NetworkingOutputSet`.
  - Is evaluated by `NetworkingProvisioningRun`.

## ManagedNetworkResourceSet

- **Purpose**: Captures the Terraform-managed network resources that enable the hosted runtime and durable session backend to share a supported GCP network path.
- **Fields**:
  - `network_reference`: reviewable network identifier for the hosted environment
  - `subnet_references`: one or more subnet identifiers used by the supported hosted path
  - `resource_ownership`: `terraform_managed` or `external`
  - `coverage_status`: `planned`, `managed`, `partial`, or `missing`
  - `review_evidence`: Terraform plan or output reference proving the resources are in scope
- **Validation Rules**:
  - `resource_ownership=terraform_managed` is required for the supported GCP path.
  - `coverage_status=managed` is required before deployment can claim durable-session readiness.
  - A partial or missing network resource set must block release readiness for hosted durable-session environments.
- **Relationships**:
  - Belongs to one `HostedNetworkingProfile`.
  - Supplies references to `CloudRunConnectivityPath`.
  - Produces evidence for `NetworkingProvisioningRun`.

## CloudRunConnectivityPath

- **Purpose**: Describes how the hosted Cloud Run runtime attaches to the managed network layer and reaches the durable session backend.
- **Fields**:
  - `runtime_attachment_reference`: reviewable identifier for the Cloud Run connectivity resource
  - `backend_network_reference`: network reference authorized for the session backend
  - `path_state`: `planned`, `attached`, `unreachable`, or `unknown`
  - `durability_required`: whether this path is mandatory for hosted readiness
  - `verification_state`: `untested`, `verified`, or `failed`
- **Validation Rules**:
  - Durable-session environments require both a runtime attachment reference and a backend network reference.
  - `path_state=attached` is required before the hosted environment can be treated as provisioned.
  - Connectivity failures must remain distinguishable from secret-access or generic deployment failures.
- **Relationships**:
  - Belongs to one `HostedNetworkingProfile`.
  - Depends on one `ManagedNetworkResourceSet`.
  - Is summarized by `NetworkingOutputSet`.

## NetworkingOutputSet

- **Purpose**: Represents the Terraform-exported networking values that downstream deployment, verification, and runbook workflows use as reviewable handoff evidence.
- **Fields**:
  - `environment`: hosted environment identifier
  - `connectivity_model`: exported hosted connectivity model
  - `network_references`: exported managed network identifiers
  - `runtime_attachment_reference`: exported Cloud Run connectivity reference
  - `session_backend_reference`: exported durable session backend reference
  - `consumption_scope`: `deploy_only`, `verify_only`, `shared_handoff`, or `documentation_only`
  - `export_status`: `missing`, `partial`, or `complete`
- **Validation Rules**:
  - `export_status=complete` is required before deployment handoff can be considered review-ready.
  - Output fields may include resource references but must not include secret values or bearer tokens.
  - The output set must provide enough information for operators to trace the managed network path without reconstructing values manually.
- **Relationships**:
  - Produced from one `HostedNetworkingProfile`.
  - Consumed by `NetworkingProvisioningRun`.
  - Referenced by deployment and hosted verification evidence.

## NetworkingProvisioningRun

- **Purpose**: Represents one end-to-end infrastructure reconciliation and review cycle for the managed hosted networking path.
- **Fields**:
  - `environment`: hosted environment under test
  - `provisioning_mode`: `healthy_path`, `missing_network_resource`, `missing_output`, or `stale_runbook`
  - `executed_steps`: ordered set of provisioning, export, deploy, and verification checks
  - `overall_result`: `pass` or `fail`
  - `first_failure_layer`: `provisioning`, `handoff`, `deployment`, `verification`, or `documentation`
  - `evidence_location`: artifact reference for plan, outputs, deployment record, or runbook review
  - `executed_at`: timestamp for the run
- **Validation Rules**:
  - A healthy path must prove both managed network provisioning and reviewable output handoff.
  - Missing managed network resources or missing outputs must fail before the hosted rollout is treated as ready.
  - A stale runbook that still requires manual networking prerequisites invalidates the supported GCP operator path.
- **Relationships**:
  - Validates one `HostedNetworkingProfile`.
  - Consumes one `NetworkingOutputSet`.
  - Produces zero or more operator-facing failure signals.

## ManualPrerequisiteBoundary

- **Purpose**: Captures the operator-visible boundary between Terraform-managed hosted networking and the prerequisites that remain outside this feature's responsibility.
- **Fields**:
  - `hosted_path`: `minimal_local`, `hosted_like_local`, or `hosted_gcp`
  - `managed_by_terraform`: list of infrastructure obligations owned by Terraform
  - `operator_managed`: list of remaining operator responsibilities
  - `boundary_status`: `clear`, `ambiguous`, or `violated`
  - `documentation_state`: `aligned`, `stale`, or `missing`
- **Validation Rules**:
  - `hosted_gcp` must classify VPC, subnet, and Cloud Run connectivity resources as Terraform-managed for the supported durable-session path.
  - `minimal_local` and `hosted_like_local` must remain free of hosted GCP networking prerequisites.
  - `boundary_status=clear` is required before the runbook can be treated as complete for this feature.
- **Relationships**:
  - References one `HostedNetworkingProfile`.
  - Is enforced through runbook and contract coverage.

## State Transitions

### Hosted Networking Profile

1. `draft` -> networking expectations recorded for the hosted environment.
2. `planned` -> managed network resources, connectivity path, and output expectations defined.
3. `provisioned` -> Terraform-managed network resources are created for the supported GCP path.
4. `exported` -> required networking outputs are emitted for deployment and verification.
5. `verified` -> deployment evidence and hosted verification confirm the managed path is reviewable and usable.
6. `failed` -> provisioning, output handoff, or documentation boundary prevents the environment from claiming durable-session readiness.

### Networking Provisioning Run

1. `plan-reviewed` -> managed network resources are in scope for the environment.
2. `resources-applied` -> Terraform-managed hosted network layer is provisioned.
3. `outputs-exported` -> networking output set is emitted for downstream consumption.
4. `deployment-evidence-reviewed` -> deploy handoff confirms the managed path is represented in rollout evidence.
5. `runbook-reviewed` -> operator guidance confirms manual network prerequisites are removed from the supported path.
6. `verified` or `failed` -> overall networking result is finalized.
