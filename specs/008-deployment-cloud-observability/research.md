# Research: FND-008 Deployment Execution + Cloud Run Observability

## Phase 0 Research Summary

### Decision: Execute the deployment command inside the existing operator workflow instead of adding a second deploy path
Rationale: The repository already has one deployment entrypoint in
`scripts/deploy_cloud_run.sh` plus validated command-building logic in
`src/mcp_server/deploy.py`. Converting that workflow from render-only output to
actual deployment execution preserves operator ergonomics and avoids parallel
deployment paths that could drift.
Alternatives considered:
- Add a second script dedicated only to execution: rejected because operators
  would need to choose between two nearly identical deploy paths.
- Keep rendering the command and require operators to run it manually: rejected
  because FND-008 explicitly requires one workflow that performs the deploy.

### Decision: Model deployment results as an explicit deployment-run record with incomplete metadata as a first-class outcome
Rationale: FND-008 requires more than command success. Operators need the
created revision, hosted URL, and applied runtime settings in one retained
record, and partial metadata capture must not be mistaken for a fully usable
deployment.
Alternatives considered:
- Treat shell success as sufficient evidence: rejected because it cannot prove
  which revision was created or whether required metadata is available.
- Capture only revision name and omit runtime settings: rejected because the
  spec requires operators to verify the deployed runtime profile without manual
  reconstruction.

### Decision: Emit hosted request logs as structured JSON through runtime stdout/stderr
Rationale: The current observability module already shapes structured request
events in memory for tests. Emitting the same normalized event shape to runtime
output is the smallest change that satisfies Cloud Logging ingestion without
adding an external logging subsystem.
Alternatives considered:
- Add a dedicated logging service or sidecar: rejected because it adds
  operational complexity outside the feature scope.
- Keep logs only in in-memory state for tests: rejected because platform
  operators cannot inspect in-memory logs from a hosted revision.

### Decision: Reuse the existing request context and event field set as the canonical hosted log schema
Rationale: Existing tests already rely on `requestId`, `path`, `status`,
`latencyMs`, and optional `toolName`. Reusing this schema preserves local and
hosted parity, reduces contract risk, and keeps log analysis straightforward.
Alternatives considered:
- Introduce a second hosted-only log schema: rejected because local and hosted
  diagnostics would diverge.
- Log only raw HTTP access lines: rejected because they do not satisfy the
  structured observability requirements in the PRD or spec.

### Decision: Keep deployment verification separate from deployment execution, but require deployment execution to produce the inputs verification needs
Rationale: FND-006 already established a hosted verification flow. FND-008
should feed that flow with a complete deployment record rather than merging
execution and verification into one opaque step.
Alternatives considered:
- Make deployment and verification a single inseparable command: rejected
  because operators need to distinguish deploy failures from post-deploy
  readiness or MCP failures.
- Leave verification input capture manual: rejected because it reintroduces the
  operator burden that FND-008 is intended to remove.

## Dependencies and Integration Patterns

- Dependency: Existing deployment input validation and command assembly in
  `src/mcp_server/deploy.py`.
  - Pattern: Reuse current validated deployment inputs and extend them with
    execution-result capture rather than rebuilding deployment configuration in
    shell.
- Dependency: Existing Cloud Run deployment shell wrapper in
  `scripts/deploy_cloud_run.sh`.
  - Pattern: Preserve the script as the single operator entrypoint while
    changing its behavior from command rendering to deploy execution plus
    metadata reporting.
- Dependency: Existing hosted request context and structured event fields in
  `src/mcp_server/observability.py`.
  - Pattern: Use the same event fields for both in-memory logs and hosted
    stdout/stderr emission so tests and production behavior stay aligned.
- Dependency: Existing hosted HTTP execution flow in
  `src/mcp_server/cloud_run_entrypoint.py`.
  - Pattern: Ensure every hosted request path routes through the same
    observability recording flow so probe, MCP, and failure traffic all emit
    comparable structured log records.
- Integration target: Cloud Run runtime metadata and operator verification
  workflow.
  - Pattern: Produce one deployment-run record containing the service URL,
    revision name, runtime settings, and deployment status so later verification
    can proceed without additional manual platform queries.

## Red-Green-Refactor Plan

### Red
- Add failing unit and integration tests proving `scripts/deploy_cloud_run.sh`
  performs deployment execution instead of printing only the command.
- Add failing tests proving successful deployment output includes revision name,
  service URL, runtime identity, environment profile, scaling bounds,
  concurrency, and timeout.
- Add failing integration and contract tests proving hosted runtime log events
  are emitted in structured form for `/healthz`, `/readyz`, `/mcp`, and
  unsupported paths, with optional `toolName` on tool calls only.

### Green
- Add the minimum deployment execution behavior needed to run the hosted deploy
  command and capture its outcome.
- Add the minimum deployment-run record needed to classify success, failure, or
  incomplete metadata capture and expose required verification inputs.
- Add the minimum runtime log emission path that writes the existing structured
  event schema to stdout/stderr while preserving current in-memory observability
  behavior.

### Refactor
- Consolidate deployment-result formatting and metadata extraction behind shared
  helpers so shell and Python code do not duplicate revision parsing logic.
- Remove any duplicate observability formatting between in-memory recording and
  hosted runtime emission.
- Re-run full regression coverage to confirm deployment verification, hosted
  semantics, MCP flows, and readiness behavior remain compatible.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. Technical planning decisions for
FND-008 are resolved within the current repository context and constitution.
