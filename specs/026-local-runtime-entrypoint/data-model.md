# Data Model: Local Runtime Ergonomics and Environment Entry Point

## Overview

FND-026 does not introduce persistent storage. The design centers on local runtime configuration entities, workflow profiles, and the verification evidence that proves the canonical local startup path behaves as intended.

## Entities

### 1. Local Startup Entry Point

- **Purpose**: Represents the canonical repository-owned way a developer starts the local MCP server.
- **Fields**:
  - `entrypoint_name`
    - Type: string
    - Required: yes
    - Meaning: stable developer-facing label for the local startup path
  - `workspace_scope`
    - Type: descriptive value
    - Required: yes
    - Meaning: indicates the entry point is executed from the repository workspace
  - `defaults_source`
    - Type: string
    - Required: yes
    - Meaning: the local environment defaults file consumed by the entry point
  - `runtime_profile`
    - Type: descriptive value
    - Required: yes
    - Allowed values: `minimal_local`, `hosted_like_local`
- **Validation rules**:
  - The entry point must support the minimal local runtime without cloud prerequisites.
  - The entry point must load the documented local defaults before server startup.
- **Relationships**:
  - Consumes one `Local Environment Defaults File`.
  - Starts one `Local Startup Attempt`.

### 2. Local Environment Defaults File

- **Purpose**: Represents the maintained local configuration baseline for local execution.
- **Fields**:
  - `file_name`
    - Type: string
    - Required: yes
  - `variable_groups`
    - Type: list of descriptive values
    - Required: yes
    - Examples: `runtime_metadata`, `local_security_defaults`, `session_defaults`, `host_runtime_settings`
  - `baseline_session_mode`
    - Type: descriptive value
    - Required: yes
    - Allowed values: `memory`
  - `override_allowed`
    - Type: boolean
    - Required: yes
  - `hosted_inputs_excluded`
    - Type: boolean
    - Required: yes
- **Validation rules**:
  - The file must define or reference the variables required for the documented minimal local workflow.
  - The file must not require hosted deployment-only inputs for baseline local startup.
- **Relationships**:
  - Is loaded by one or more `Local Startup Entry Point` executions.
  - May be partially overridden by one `Hosted-Like Override Set`.

### 3. Hosted-Like Override Set

- **Purpose**: Represents the local-only changes needed to switch from the baseline local mode to durable-session verification mode.
- **Fields**:
  - `selection_trigger`
    - Type: descriptive value
    - Required: yes
    - Meaning: how the hosted-like local mode is selected
  - `session_backend`
    - Type: descriptive value
    - Required: yes
    - Allowed values: `redis`
  - `session_store_reference`
    - Type: string
    - Required: yes
  - `durability_required`
    - Type: boolean
    - Required: yes
  - `connectivity_model`
    - Type: descriptive value
    - Required: yes
- **Validation rules**:
  - Hosted-like overrides may be applied only when the supporting dependency path is available.
  - Hosted-like overrides must remain scoped to local verification and must not redefine the minimal local baseline.
- **Relationships**:
  - Extends one `Local Environment Defaults File`.
  - Requires one `Local Dependency Bootstrap`.

### 4. Local Dependency Bootstrap

- **Purpose**: Represents the supporting local dependency workflow used for hosted-like local verification.
- **Fields**:
  - `dependency_type`
    - Type: descriptive value
    - Required: yes
    - Meaning: shared durable session dependency used locally
  - `startup_command`
    - Type: string
    - Required: yes
  - `shutdown_command`
    - Type: string
    - Required: yes
  - `failure_guidance_present`
    - Type: boolean
    - Required: yes
- **Validation rules**:
  - The bootstrap workflow must be documented separately from the minimal local runtime.
  - Failure guidance must explain how to recover when the dependency is not available.
- **Relationships**:
  - Enables one `Hosted-Like Override Set`.
  - Produces evidence for one `Local Verification Record`.

### 5. Local Startup Attempt

- **Purpose**: Represents one developer attempt to start the server locally through the canonical entry point.
- **Fields**:
  - `profile`
    - Type: descriptive value
    - Required: yes
    - Allowed values: `minimal_local`, `hosted_like_local`
  - `defaults_loaded`
    - Type: boolean
    - Required: yes
  - `dependency_ready`
    - Type: boolean
    - Required: no
    - Meaning: relevant only for hosted-like local mode
  - `startup_status`
    - Type: descriptive value
    - Required: yes
    - Allowed values: `started`, `blocked`, `failed`
  - `failure_category`
    - Type: string
    - Required: no
    - Examples: `missing_defaults_file`, `missing_dependency`, `invalid_override`
- **Validation rules**:
  - Minimal local attempts must not fail due to missing hosted dependencies.
  - Hosted-like local attempts must fail clearly when required dependencies are unavailable.
- **Relationships**:
  - Uses one `Local Startup Entry Point`.
  - Produces one `Local Verification Record`.

### 6. Local Verification Record

- **Purpose**: Captures evidence that the documented local workflow behaves according to the contract.
- **Fields**:
  - `check_name`
    - Type: string
    - Required: yes
  - `profile`
    - Type: descriptive value
    - Required: yes
  - `result`
    - Type: success/fail outcome
    - Required: yes
  - `evidence_type`
    - Type: descriptive value
    - Required: yes
    - Examples: `documentation_check`, `contract_test`, `startup_result`
  - `notes`
    - Type: descriptive text
    - Required: yes
- **Validation rules**:
  - Evidence must distinguish minimal local success from hosted-like local success or failure conditions.
  - Failure-path evidence must include clear remediation guidance.

## Relationships Summary

- One `Local Startup Entry Point` loads one `Local Environment Defaults File`.
- One `Local Environment Defaults File` defines the baseline for the `minimal_local` profile.
- One `Hosted-Like Override Set` extends the baseline defaults and depends on one `Local Dependency Bootstrap`.
- One `Local Startup Attempt` uses the entry point with either the baseline profile or the hosted-like override profile.
- One `Local Verification Record` proves the outcome of a startup attempt or documentation-backed contract check.

## State Transitions

### Minimal Local Runtime

1. Developer invokes the `Local Startup Entry Point`.
2. The `Local Environment Defaults File` is loaded.
3. The `minimal_local` profile is selected.
4. The local server starts without shared-session dependency requirements.
5. Verification records show the local endpoint is available.

### Hosted-Like Local Verification

1. Developer starts the `Local Dependency Bootstrap`.
2. Developer selects the `Hosted-Like Override Set`.
3. The same `Local Startup Entry Point` loads the baseline defaults and applies hosted-like overrides.
4. The local server starts with durable-session behavior enabled.
5. Verification records show the hosted-like local profile is available.

### Hosted-Like Failure Path

1. Developer selects the hosted-like local profile.
2. Required dependency bootstrap is missing or unreachable.
3. The `Local Startup Attempt` ends in `blocked` or `failed`.
4. Failure guidance identifies the missing prerequisite and the recovery step.
