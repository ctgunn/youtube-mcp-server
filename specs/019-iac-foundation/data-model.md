# Data Model: Infrastructure as Code Foundation

## Infrastructure Stack

- **Purpose**: Represents the versioned infrastructure definition set for one provider and one environment.
- **Fields**:
  - `provider`: infrastructure provider identifier, initially `gcp`
  - `environment`: `dev`, `staging`, or `prod`
  - `service_name`: hosted MCP service name
  - `project_id`: cloud project/account identifier
  - `region`: target hosted region
  - `runtime_identity`: service account or runtime identity used by the hosted service
  - `min_instances`: minimum hosted capacity setting
  - `max_instances`: maximum hosted capacity setting
  - `concurrency`: hosted request concurrency setting
  - `timeout_seconds`: hosted request timeout setting
  - `status`: `defined`, `planned`, `applied`, `failed`, or `retired`
- **Validation Rules**:
  - `environment` must be one of the supported runtime profiles.
  - `service_name`, `project_id`, `region`, and `runtime_identity` are required for hosted provisioning.
  - `min_instances` must be greater than or equal to `0`.
  - `max_instances` must be greater than or equal to `min_instances`.
  - `concurrency` and `timeout_seconds` must be positive integers.
- **Relationships**:
  - Owns one or more `Secret Bindings`.
  - Owns one `Session Backend Endpoint`.
  - Produces one `Deployment Input Profile`.

## Secret Binding

- **Purpose**: Describes a secret-backed runtime input required by the hosted service.
- **Fields**:
  - `name`: logical secret name, such as `YOUTUBE_API_KEY` or `MCP_AUTH_TOKEN`
  - `required_profiles`: environments in which the secret must be available
  - `injection_target`: runtime variable or integration point that consumes the secret
  - `source_reference`: provider-managed secret reference used during deployment
  - `status`: `declared`, `bound`, `missing`, or `invalid`
- **Validation Rules**:
  - Every secret required by `staging` or `prod` must be declared in the infrastructure contract.
  - Secret values must never be stored in versioned artifacts.
- **Relationships**:
  - Belongs to one `Infrastructure Stack`.
  - Is consumed by one `Deployment Input Profile`.

## Session Backend Endpoint

- **Purpose**: Represents the shared-state dependency needed for durable hosted MCP sessions.
- **Fields**:
  - `backend_type`: `redis` for hosted durability, `memory` for minimal local runtime, or `redis-local` for hosted-like local verification
  - `connection_reference`: secret-backed connection reference or local connection URL
  - `durability_required`: whether readiness and hosted verification require the backend to be healthy
  - `session_ttl_seconds`: inactive session retention interval
  - `replay_ttl_seconds`: reconnect replay retention interval
  - `scope`: `minimal_local`, `hosted_like_local`, or `hosted`
  - `status`: `planned`, `ready`, `unavailable`, or `retired`
- **Validation Rules**:
  - Hosted durability requires a shared backend rather than a process-local backend.
  - TTL values must be positive integers when specified.
  - `connection_reference` is required for `redis` and `redis-local`.
- **Relationships**:
  - Belongs to one `Infrastructure Stack` for hosted use.
  - Is referenced by one or more `Verification Paths`.

## Deployment Input Profile

- **Purpose**: Captures the operator-facing values that connect provisioned infrastructure to the application deployment workflow.
- **Fields**:
  - `environment`
  - `service_name`
  - `image_reference`
  - `region`
  - `project_id`
  - `service_account_email`
  - `secret_reference_names`
  - `config_values`
  - `session_backend`
  - `session_store_reference`
  - `status`: `draft`, `validated`, `deployed`, or `rejected`
- **Validation Rules**:
  - Must include all fields required by `scripts/deploy_cloud_run.sh`.
  - Must express environment-specific differences through injectable values rather than source changes.
  - Must distinguish secret references from non-secret config values.
- **Relationships**:
  - Produced by one `Infrastructure Stack`.
  - Consumed by one `Provisioning Runbook`.

## Verification Path

- **Purpose**: Defines a reproducible operator or developer workflow for proving the service is usable in a given execution mode.
- **Fields**:
  - `mode`: `minimal_local`, `hosted_like_local`, or `hosted`
  - `prerequisites`: required tools, dependencies, and environment inputs
  - `commands`: documented commands or workflow steps
  - `expected_outputs`: evidence artifacts or observable success signals
  - `failure_guidance`: the first place an operator should look when the path fails
  - `status`: `defined`, `documented`, `verified`, or `outdated`
- **Validation Rules**:
  - `minimal_local` must not require cloud provisioning.
  - `hosted_like_local` must explicitly declare any extra dependency startup steps.
  - `hosted` must consume provisioned infrastructure outputs and deployment outputs.
- **Relationships**:
  - May depend on one `Session Backend Endpoint`.
  - References one `Deployment Input Profile` for hosted verification.

## State Transitions

- **Infrastructure Stack**: `defined -> planned -> applied -> failed|retired`
- **Secret Binding**: `declared -> bound -> missing|invalid`
- **Session Backend Endpoint**: `planned -> ready -> unavailable|retired`
- **Deployment Input Profile**: `draft -> validated -> deployed|rejected`
- **Verification Path**: `defined -> documented -> verified|outdated`
