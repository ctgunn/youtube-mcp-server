# Data Model: Hosted Dependency Wiring for Secrets and Durable Sessions

## HostedDependencyProfile

- **Purpose**: Represents one hosted environment's operator-visible dependency wiring state for runtime secret access and durable session support.
- **Fields**:
  - `environment`: hosted environment identifier such as `dev`, `staging`, or `prod`
  - `service_name`: hosted service identifier
  - `runtime_identity`: runtime service identity reference used by the hosted service
  - `secret_access_mode`: operator-visible model for how required secrets are supplied to the runtime
  - `session_backend_type`: `redis` for durable hosted sessions
  - `durability_required`: whether hosted readiness requires a healthy shared session backend
  - `status`: `draft`, `wired`, `verified`, `degraded`, or `failed`
- **Validation Rules**:
  - `runtime_identity` is required for hosted deployment.
  - `secret_access_mode` must identify a reviewable secret-backed runtime path.
  - `session_backend_type=redis` is required for hosted environments claiming durable sessions.
- **Relationships**:
  - Owns one or more `SecretAccessBinding` records.
  - Owns one `SessionConnectivityPath`.
  - Is evaluated by `DependencyVerificationRun`.

## SecretAccessBinding

- **Purpose**: Describes the permission and reference path that allows the hosted runtime identity to read one required secret-backed runtime input.
- **Fields**:
  - `secret_name`: logical secret name such as `YOUTUBE_API_KEY` or `MCP_AUTH_TOKEN`
  - `runtime_identity`: identity expected to read the secret
  - `required_profiles`: hosted profiles in which the secret is mandatory
  - `access_scope`: least-privilege access level required for runtime use
  - `reference_status`: `declared`, `bound`, `missing`, or `invalid`
  - `verification_state`: `untested`, `verified`, or `failed`
- **Validation Rules**:
  - Every secret required by a hosted environment must map to one runtime identity.
  - Secret names and access bindings may appear in review artifacts, but secret values must never appear.
  - `failed` verification must produce operator-visible remediation guidance.
- **Relationships**:
  - Belongs to one `HostedDependencyProfile`.
  - Produces zero or one `DependencyFailureSignal`.

## SessionConnectivityPath

- **Purpose**: Represents the provider-specific path that allows the hosted runtime to reach the durable session backend needed for hosted session continuity.
- **Fields**:
  - `backend_type`: `redis`
  - `connection_reference`: non-secret reference to the hosted session endpoint
  - `network_path_model`: operator-visible description of the provider-specific connectivity path
  - `durability_required`: whether readiness must fail when the backend is unreachable
  - `connectivity_state`: `planned`, `reachable`, `unreachable`, or `unknown`
  - `verification_state`: `untested`, `verified`, or `failed`
- **Validation Rules**:
  - Hosted durable-session environments require `backend_type=redis`.
  - `connection_reference` and `network_path_model` are required for hosted connectivity planning.
  - `unreachable` connectivity must produce a distinct failure classification from secret-access failure.
- **Relationships**:
  - Belongs to one `HostedDependencyProfile`.
  - Is consumed by `DependencyReadinessState`.
  - Produces zero or one `DependencyFailureSignal`.

## DependencyReadinessState

- **Purpose**: Captures the operator-visible readiness summary for hosted dependency wiring after startup and during verification.
- **Fields**:
  - `configuration_check`: `pass` or `fail`
  - `secret_access_check`: `pass` or `fail`
  - `runtime_check`: `pass` or `fail`
  - `session_connectivity_check`: `pass` or `fail`
  - `overall_status`: `ready` or `not_ready`
  - `primary_reason_code`: dominant readiness failure code, if any
  - `evaluated_at`: timestamp of the readiness evaluation
- **Validation Rules**:
  - `overall_status=ready` requires all dependency checks needed by the hosted mode to pass.
  - Secret-access failure and session-connectivity failure must remain distinguishable through `primary_reason_code`.
  - No readiness artifact may expose secret values.
- **Relationships**:
  - Evaluates one `HostedDependencyProfile`.
  - References one or more `DependencyFailureSignal` records when not ready.

## DependencyFailureSignal

- **Purpose**: Captures the operator-visible interpretation of a hosted dependency failure.
- **Fields**:
  - `failure_layer`: `secret_access` or `session_connectivity`
  - `failure_category`: `missing_permission`, `missing_reference`, `invalid_reference`, `backend_unreachable`, `backend_unconfigured`, or `dependency_client_unavailable`
  - `request_impact`: `startup_blocked`, `readiness_failed`, or `session_continuation_at_risk`
  - `recommended_remediation`: operator-facing next action
  - `observed_in`: readiness check, hosted verification step, or deployment evidence review
- **Validation Rules**:
  - `failure_layer=secret_access` must not be used for connectivity-only failures.
  - `failure_layer=session_connectivity` must not be used for secret reference or permission failures.
  - Every failure signal must map to one remediation path.
- **Relationships**:
  - May be produced by `SecretAccessBinding`, `SessionConnectivityPath`, or `DependencyReadinessState`.
  - Is recorded by `DependencyVerificationRun`.

## DependencyVerificationRun

- **Purpose**: Represents the ordered hosted verification flow that proves a deployment has working dependency wiring or diagnoses the first wiring failure.
- **Fields**:
  - `service_name`: hosted service under test
  - `revision_name`: hosted revision or deployment record under test
  - `verification_mode`: `healthy_path`, `secret_failure`, or `session_failure`
  - `executed_checks`: ordered set of verification checks
  - `overall_result`: `pass` or `fail`
  - `evidence_location`: file or artifact reference holding the verification output
  - `executed_at`: timestamp of the verification run
- **Validation Rules**:
  - The healthy path must prove both secret access and session continuity for environments claiming durable hosted session support.
  - Failure modes must identify whether the first dependency failure is secret-related or session-connectivity-related.
  - Verification evidence must remain free of secret values and bearer tokens.
- **Relationships**:
  - Validates one `HostedDependencyProfile`.
  - Produces zero or more `DependencyFailureSignal` records.

## State Transitions

### Hosted Dependency Profile

1. `draft` -> dependency expectations recorded for an environment.
2. `wired` -> provider-specific secret and session paths are configured.
3. `verified` -> hosted verification proves the wiring works.
4. `degraded` -> one dependency path fails after being wired.
5. `failed` -> deployment cannot be treated as ready for the claimed hosted mode.

### Dependency Verification

1. `deployment_recorded` -> hosted revision and dependency profile available.
2. `secret_access_checked` -> runtime secret path verified or failed.
3. `session_connectivity_checked` -> durable session connectivity verified or failed.
4. `session_continuation_checked` -> hosted continuation flow verified when applicable.
5. `diagnosed` -> failure layer and remediation path recorded for the first failing dependency.
6. `verified` or `failed` -> overall hosted dependency result finalized.
