# Data Model: Cloud Run Public Reachability for Remote MCP

## CloudRunPublicAccessPolicy

- **Purpose**: Represents the operator-visible decision about whether a hosted Cloud Run environment is intended to accept trusted remote MCP traffic from the public Internet.
- **Fields**:
  - `environment`: hosted environment identifier such as `dev`, `staging`, or `prod`
  - `public_invocation_intent`: `public_remote_mcp` or `private_only`
  - `service_name`: hosted service identifier
  - `connection_point`: published service URL or equivalent remote consumer endpoint
  - `review_evidence_required`: whether rollout artifacts must prove public reachability
  - `declared_at`: timestamp or release context when the policy was recorded
- **Validation Rules**:
  - `public_invocation_intent=public_remote_mcp` requires a documented `connection_point`.
  - `public_invocation_intent=private_only` must not be described as supporting trusted public remote consumers.
  - Policy intent must be visible in operator-facing review artifacts before rollout.
- **Relationships**:
  - Feeds `DeploymentExposureRecord`.
  - Is validated by `ReachabilityVerificationRun`.

## DeploymentExposureRecord

- **Purpose**: Captures the hosted deployment outputs and exposure intent that reviewers and operators use to determine whether a revision is meant to be publicly reachable.
- **Fields**:
  - `revision_name`: deployed hosted revision identifier
  - `service_name`: hosted service name
  - `connection_point`: published hosted URL
  - `runtime_identity`: runtime service identity reference
  - `public_invocation_intent`: copied exposure intent from the deployment workflow
  - `runtime_settings_summary`: non-secret hosted settings visible in deployment evidence
  - `recorded_at`: timestamp when deployment evidence was emitted
- **Validation Rules**:
  - `connection_point` must be present for every hosted deployment record.
  - `public_invocation_intent` must match the intended environment exposure policy.
  - Secret values and bearer tokens must never appear in the record.
- **Relationships**:
  - Produced by the deployment workflow.
  - Consumed by `ReachabilityVerificationRun`.

## ReachabilityVerificationRun

- **Purpose**: Represents the ordered operator-facing verification that proves public reachability and distinguishes platform denial from MCP-layer denial.
- **Fields**:
  - `revision_name`: hosted revision under test
  - `connection_point`: hosted endpoint being verified
  - `verification_mode`: `public_reachability`, `mcp_authenticated`, or `denial_diagnostics`
  - `overall_result`: `pass` or `fail`
  - `executed_checks`: ordered set of check names
  - `evidence_location`: file or artifact reference holding the verification output
  - `executed_at`: timestamp of the verification run
- **Validation Rules**:
  - Checks must preserve the order `reachability` before authenticated MCP checks.
  - A failed reachability prerequisite must prevent the run from reporting authenticated MCP success.
  - Evidence must describe the remediation path for the first failed check.
- **Relationships**:
  - Validates one `DeploymentExposureRecord`.
  - Produces one or more `AccessFailureSignal` records.

## AccessFailureSignal

- **Purpose**: Captures the operator-visible interpretation of a failed hosted access attempt.
- **Fields**:
  - `failure_layer`: `cloud_platform` or `mcp_application`
  - `failure_category`: `public_access_denied`, `unauthenticated`, `invalid_credential`, `origin_denied`, `malformed_security_input`, or `unsupported_request`
  - `status_family`: response family or equivalent operator-visible signal
  - `request_reached_application`: whether the request reached the hosted MCP runtime
  - `recommended_remediation`: operator-facing next action
  - `observed_in`: verification check or runbook step where the signal was captured
- **Validation Rules**:
  - `failure_layer=cloud_platform` requires `request_reached_application=false`.
  - MCP-layer categories may only be used when `request_reached_application=true`.
  - Every failure signal must map to one remediation path.
- **Relationships**:
  - Produced during `ReachabilityVerificationRun`.
  - References the existing hosted security contract for MCP-layer categories.

## RemoteConsumerConnection

- **Purpose**: Represents the external caller interaction with the hosted service once public reachability has been enabled.
- **Fields**:
  - `client_type`: `trusted_remote_non_browser` or `approved_browser`
  - `target_connection_point`: hosted URL being used
  - `auth_state`: `not_attempted`, `accepted`, or `denied`
  - `origin_state`: `not_sent`, `approved`, or `denied`
  - `session_state`: `not_started`, `initialized`, or `rejected`
- **Validation Rules**:
  - `auth_state=accepted` requires the request to have reached the application layer.
  - Browser callers may only transition to `approved` origin state when their origin is permitted.
  - `session_state=initialized` requires successful authenticated MCP initialization.
- **Relationships**:
  - Interacts with `CloudRunPublicAccessPolicy`.
  - Produces `AccessFailureSignal` when denied.

## State Transitions

### Public Access Policy

1. `draft` -> exposure intent proposed for an environment.
2. `reviewed` -> public or private intent validated in release artifacts.
3. `active` -> deployment and verification use the approved intent.
4. `changed` -> exposure intent updated and must be re-verified.

### Hosted Reachability Verification

1. `deployment_recorded` -> hosted revision and connection point available.
2. `reachability_checked` -> operator proves the service is or is not publicly reachable.
3. `mcp_auth_checked` -> authenticated MCP request succeeds or fails after reachability is known.
4. `diagnosed` -> failure layer and remediation path are recorded.
5. `verified` or `failed` -> overall hosted result finalized.
