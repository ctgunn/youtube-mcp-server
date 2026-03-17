# Research: FND-012 Hosted Runtime Migration for Streaming MCP

## Phase 0 Research Summary

### Decision: Migrate the hosted runtime to an ASGI stack built around FastAPI and Uvicorn
Rationale: FND-012 exists because the current `http.server` entrypoint is too
minimal for a production-grade hosted streaming surface. The repository already
tracks FastAPI, Pydantic v2, and Uvicorn in its technology direction, and an
ASGI stack gives the project a straightforward path for streaming responses,
lifespan hooks, and Cloud Run-friendly request serving without inventing a
custom runtime framework.
Alternatives considered:
- Keep `ThreadingHTTPServer`: rejected because the feature exists specifically
  to move away from the current minimal runtime.
- Introduce a different framework stack: rejected because it would add tool and
  maintenance churn without a stronger fit than the repository's stated
  direction.

### Decision: Preserve the existing MCP request handling boundary and adapt it into the new hosted runtime rather than rewriting transport logic during the migration
Rationale: The current hosted behavior is already covered by contract and
integration tests through `execute_hosted_request`, `transport/http.py`, and
`transport/streaming.py`. Wrapping that boundary in an ASGI runtime keeps the
migration focused on runtime behavior, reduces regression risk, and preserves
FND-009 through FND-011 protocol semantics.
Alternatives considered:
- Rewrite hosted request routing directly against the framework request model:
  rejected because it expands scope into transport and protocol behavior that
  this feature is supposed to preserve.
- Stand up a separate gateway process in front of the existing runtime:
  rejected because it adds architectural complexity without user value.

### Decision: Keep `/mcp`, `/health`, and `/ready` as stable externally visible routes during and after the migration
Rationale: The spec requires downstream consumers and operators to avoid a URL
or route migration. Preserving the existing hosted paths also keeps deployed
verification, documentation, and smoke tests consistent across the runtime
change.
Alternatives considered:
- Introduce a new runtime-specific path layout: rejected because it creates
  avoidable consumer migration work.
- Collapse operational routes into framework-specific defaults: rejected
  because it would break prior acceptance criteria and deployment checks.

### Decision: Model readiness around explicit runtime startup completion instead of process start alone
Rationale: A streaming-capable runtime can accept traffic before all runtime
dependencies are actually ready if startup state is not modeled carefully. The
project already distinguishes liveness from readiness, so the migrated runtime
should continue to report alive early while withholding readiness until startup
initialization has completed successfully.
Alternatives considered:
- Treat process start as ready: rejected because it weakens operational safety
  and conflicts with the existing readiness contract.
- Block liveness until startup completes: rejected because it hides whether the
  process is alive but still initializing.

### Decision: Update container and Cloud Run startup artifacts to launch the ASGI runtime directly, while preserving one documented operator entrypoint per environment
Rationale: FND-012 includes container startup and deployment artifacts in
scope. The runtime migration only delivers user value if local startup,
container launch, and Cloud Run execution all use the new runtime consistently.
Preserving one documented entrypoint per environment keeps operations simple
and supports a clean rollback to the prior launch command if verification
fails.
Alternatives considered:
- Keep the old container command and spawn the new runtime indirectly:
  rejected because it obscures the operational entrypoint and complicates
  rollback/debugging.
- Maintain multiple supported hosted launch paths indefinitely: rejected
  because it creates drift and operational ambiguity.

### Decision: Drive the migration with failing runtime, readiness, and verification tests before changing the serving stack
Rationale: The constitution requires Red-Green-Refactor. Existing unit,
integration, and contract tests already cover hosted request handling,
readiness, and deployment assets, so the correct way to implement FND-012 is to
rewrite those expectations first to fail on the current runtime limitations and
then make the smallest runtime and deployment changes needed to pass.
Alternatives considered:
- Migrate the runtime first and add tests afterward: rejected by the
  constitution and likely to mask regressions.
- Limit the feature to manual hosted verification only: rejected because the
  runtime migration affects critical hosted behavior and needs automated
  coverage.

### Decision: Preserve structured logging and request correlation across the runtime migration, with rollback based on the previous launch command until hosted verification passes
Rationale: The constitution requires observability and a mitigation strategy
for breaking behavior. The migration must therefore keep request IDs, hosted
path/status logging, and verification evidence intact, and the rollout plan
must allow operators to revert to the prior hosted command if the migrated
runtime fails local or Cloud Run verification.
Alternatives considered:
- Accept temporary observability gaps during migration: rejected because they
  would make hosted failures materially harder to diagnose.
- Treat runtime migration as irreversible once merged: rejected because Cloud
  Run deployment verification is explicitly part of the feature.

## Dependencies and Integration Patterns

- Dependency: Current hosted entrypoint in `src/mcp_server/cloud_run_entrypoint.py`.
  - Pattern: Reuse the request-execution boundary for route behavior while
    replacing the outer server runtime with an ASGI app.
- Dependency: Current MCP transport modules in `src/mcp_server/transport/http.py`
  and `src/mcp_server/transport/streaming.py`.
  - Pattern: Keep transport/session rules intact and validate that the new
    runtime only changes serving behavior, not MCP semantics.
- Dependency: Current readiness and observability modules in
  `src/mcp_server/health.py`, `src/mcp_server/config.py`, and
  `src/mcp_server/observability.py`.
  - Pattern: Preserve liveness/readiness semantics and structured request logs
    across the runtime migration.
- Dependency: Deployment artifacts in `Dockerfile`, `scripts/deploy_cloud_run.sh`,
  and `scripts/verify_cloud_run_foundation.py`.
  - Pattern: Update startup/runtime invocation while keeping one Cloud Run
    deployment workflow and one verification workflow.

## Red-Green-Refactor Plan

### Red
- Add failing unit tests for runtime lifecycle state, readiness transitions, and
  hosted request bridging under the migrated runtime boundary.
- Add failing contract tests for `/mcp`, `/health`, and `/ready` continuity
  under the new runtime entrypoint.
- Add failing integration tests for concurrent streaming requests, hosted
  verification flow, and structured request logging after runtime migration.
- Add failing deployment-asset checks for the new container start command and
  documented local startup path.

### Green
- Introduce the minimum ASGI runtime, startup lifecycle, and route wiring needed
  to serve the existing hosted MCP behavior.
- Update readiness initialization, container startup, deployment assets, and
  local verification documentation to align with the new runtime.
- Preserve current MCP request, error, and streaming behavior while making the
  new runtime-focused tests pass.

### Refactor
- Consolidate duplicated request adaptation and lifecycle initialization logic
  between the runtime entrypoint and existing transport helpers.
- Remove transitional runtime compatibility code and stale `http.server`-only
  assumptions from deployment and verification assets.
- Re-run the full regression suite and local/hosted verification flow before
  considering the migration complete.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. The spec, constitution, current repo
state, and repository technology direction provide enough context to plan the
runtime migration.
