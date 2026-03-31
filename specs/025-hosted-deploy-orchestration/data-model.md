# Data Model: Automated Hosted Deployment Orchestration

## DeploymentBranch

- **Purpose**: Represents the repository branch whose qualifying pushes may trigger automated hosted deployment.
- **Fields**:
  - `name`: branch identifier used by the workflow trigger
  - `trigger_policy`: description of which push events qualify for deployment
  - `environment_target`: hosted environment associated with the branch
  - `status`: `inactive`, `ready`, or `blocked`
- **Validation Rules**:
  - `name` must identify exactly one intended deployment branch.
  - `environment_target` must map to one hosted deployment path.
  - `blocked` status requires at least one unmet bootstrap prerequisite.
- **Relationships**:
  - Starts zero or more `DeploymentWorkflowRun` records.
  - Depends on one or more `BootstrapPrerequisite` records.

## DeploymentWorkflowRun

- **Purpose**: Represents one end-to-end execution of the push-triggered hosted deployment workflow for a specific revision.
- **Fields**:
  - `run_id`: unique workflow-run identifier
  - `revision_ref`: commit or revision being deployed
  - `triggered_by`: qualifying push event descriptor
  - `started_at`: workflow start time
  - `completed_at`: workflow completion time
  - `overall_result`: `pass`, `fail`, or `incomplete`
  - `failed_stage`: `quality_gate`, `image_publish`, `infrastructure_reconcile`, `deploy`, `metadata_capture`, `hosted_verification`, or `none`
- **Validation Rules**:
  - Every qualifying push creates at most one `DeploymentWorkflowRun`.
  - `overall_result=pass` requires all required stages to pass.
  - `failed_stage` must be present when `overall_result=fail`.
- **Relationships**:
  - Belongs to one `DeploymentBranch`.
  - Owns ordered `WorkflowStageResult` records.
  - Produces one `DeploymentRecord`.
  - Produces zero or one `HostedVerificationGate`.

## WorkflowStageResult

- **Purpose**: Captures the observable outcome of one stage within a deployment workflow run.
- **Fields**:
  - `stage_name`: `quality_gate`, `image_publish`, `infrastructure_reconcile`, `terraform_output_export`, `deploy`, or `hosted_verification`
  - `result`: `pass`, `fail`, or `skipped`
  - `started_at`: stage start time
  - `completed_at`: stage completion time
  - `summary`: operator-readable stage outcome
  - `artifact_reference`: optional path or identifier for stage evidence
- **Validation Rules**:
  - Required stages must execute in a stable order.
  - `deploy` cannot pass before `infrastructure_reconcile` and `terraform_output_export` pass.
  - `hosted_verification` cannot pass before `deploy` passes and a deployment record exists.
- **Relationships**:
  - Belongs to one `DeploymentWorkflowRun`.
  - May reference one `InfrastructureReconciliationOutput`, `DeploymentRecord`, or `HostedVerificationGate`.

## InfrastructureReconciliationOutput

- **Purpose**: Represents the deployment-ready values emitted after infrastructure reconciliation and consumed by the application rollout path.
- **Fields**:
  - `environment`: hosted environment name
  - `service_name`: hosted service identifier
  - `runtime_identity`: runtime service identity reference
  - `public_invocation_intent`: declared hosted reachability mode
  - `secret_reference_names`: declared runtime secret references
  - `session_backend_reference`: non-secret hosted session dependency reference
  - `output_location`: artifact path containing the exported values
  - `status`: `missing`, `exported`, or `invalid`
- **Validation Rules**:
  - `output_location` must exist before the deploy stage starts.
  - Required hosted runtime values must be present when `status=exported`.
  - Secret references may be named, but secret values must never appear in the artifact.
- **Relationships**:
  - Belongs to one `DeploymentWorkflowRun`.
  - Feeds one `DeploymentRecord`.

## DeploymentRecord

- **Purpose**: Represents the structured deployment outcome emitted by the repository deployment path for one hosted rollout.
- **Fields**:
  - `deployment_id`: repository-generated deployment identifier
  - `outcome`: `success`, `failed`, or `incomplete`
  - `revision_name`: hosted revision identifier
  - `service_url`: deployed hosted service URL
  - `failure_stage`: repository deployment failure classification
  - `runtime_settings_summary`: non-secret runtime deployment summary
  - `record_location`: artifact path for the serialized deployment record
- **Validation Rules**:
  - `outcome=success` requires both `revision_name` and `service_url`.
  - `outcome=failed` or `outcome=incomplete` must carry a failure summary.
  - No secret values or bearer tokens may appear in the serialized record.
- **Relationships**:
  - Belongs to one `DeploymentWorkflowRun`.
  - Supplies inputs to one `HostedVerificationGate`.

## HostedVerificationGate

- **Purpose**: Represents the post-rollout verification decision that determines whether the deployment workflow may report success.
- **Fields**:
  - `verification_result`: `pass` or `fail`
  - `first_failure_layer`: `cloud_platform`, `secret_access`, `session_connectivity`, `application_runtime`, `mcp_auth`, or `none`
  - `evidence_location`: artifact path for hosted verification evidence
  - `checked_contracts`: ordered list of verification checks performed
  - `completed_at`: verification completion time
- **Validation Rules**:
  - `verification_result=pass` requires all required hosted checks to pass.
  - `verification_result=fail` requires a first failed check and remediation path.
  - A deployment workflow run cannot finish with `overall_result=pass` unless `verification_result=pass`.
- **Relationships**:
  - Belongs to one `DeploymentWorkflowRun`.
  - Consumes one `DeploymentRecord`.

## BootstrapPrerequisite

- **Purpose**: Represents one one-time operator-managed requirement that must exist before push-triggered deployment can run reliably.
- **Fields**:
  - `name`: prerequisite identifier
  - `category`: `repository_automation`, `cloud_access`, `secret_population`, or `artifact_destination`
  - `owner`: `operator` or `automation`
  - `required_before_stage`: earliest stage blocked by the prerequisite
  - `state`: `pending`, `satisfied`, or `blocked`
  - `remediation`: operator-facing next action
- **Validation Rules**:
  - Operator-owned prerequisites cannot be silently assumed by automation.
  - `secret_population` prerequisites may describe required secret values but must not include the values themselves.
  - Any `pending` prerequisite that blocks an early stage must surface a failing workflow outcome.
- **Relationships**:
  - May block one `DeploymentBranch`.
  - May cause one `DeploymentWorkflowRun` to fail early.

## State Transitions

### Deployment Workflow Run

1. `queued` -> qualifying push accepted for the deployment branch.
2. `quality_gate_running` -> repository test and lint checks start.
3. `image_publish_running` -> deployable image for the pushed revision is being built and published.
4. `infrastructure_reconcile_running` -> hosted infrastructure is being reconciled.
5. `deploy_running` -> the repository deployment path is rolling out the current revision.
6. `verification_running` -> hosted verification is proving the deployed MCP endpoint.
7. `pass`, `fail`, or `incomplete` -> final workflow result is recorded.

### Bootstrap Prerequisite

1. `pending` -> prerequisite is known but not yet prepared.
2. `satisfied` -> prerequisite is in place for the intended environment.
3. `blocked` -> prerequisite is missing or invalid and prevents safe automation.

### Hosted Verification Gate

1. `waiting_for_record` -> deployment record not yet available.
2. `running` -> hosted verification checks are executing.
3. `pass` -> rollout may be treated as successful.
4. `fail` -> rollout remains unsuccessful until the failure is corrected and re-run.
