# Research: FND-006 Cloud Run Foundation Deployment

## Phase 0 Research Summary

### Decision: Deploy the existing MCP foundation service as a single containerized web service revision
Rationale: The current codebase is a single Python service with one runtime entrypoint and no separate worker or control-plane components. A single hosted revision is the smallest deployment unit that satisfies the feature scope.
Alternatives considered:
- Split deployment into separate MCP and operational services: rejected because current behavior is served by one process and the added topology does not provide user value for FND-006.
- Delay containerization until YouTube tools exist: rejected because the PRD makes hosted foundation deployment the gate before tool work.

### Decision: Treat deployment inputs as an explicit, validated release surface
Rationale: FND-006 requires reproducible operator behavior. Runtime identity, scaling bounds, concurrency, timeout, environment profile, build metadata, and secret references must be declared and reviewed together to avoid ad hoc deployment drift.
Alternatives considered:
- Rely on undocumented platform defaults: rejected because defaults are easy to miss and do not satisfy reproducibility requirements.
- Validate only environment variables and ignore revision settings: rejected because scaling and timeout settings are part of the acceptance criteria.

### Decision: Use post-deploy verification as the proof of completion for a hosted revision
Rationale: A revision is not meaningfully complete unless it passes `/healthz`, `/readyz`, MCP initialize, tool discovery, and baseline tool invocation on the hosted endpoint.
Alternatives considered:
- Accept successful deployment command execution as sufficient: rejected because it does not prove the hosted service is serving MCP traffic correctly.
- Verify only health endpoints: rejected because FND-006 explicitly requires MCP round-trip validation.

### Decision: Preserve the current MCP and operational contracts while adding deployment-specific verification evidence
Rationale: FND-006 is a deployment slice, not a protocol redesign. The safest path is to keep the service contract stable and add operator-facing deployment evidence around it.
Alternatives considered:
- Introduce deployment-only protocol changes to expose revision data: rejected because deployment evidence can be captured outside the runtime contract.
- Expand baseline tools just for deployment diagnostics: rejected because FND-006 only needs proof that existing baseline tools work when hosted.

### Decision: Keep deployment verification evidence lightweight and file/document oriented
Rationale: The current project already relies on repository documentation and automated tests. Storing required evidence as documented outputs and reproducible commands is sufficient for this slice without adding a new tracking subsystem.
Alternatives considered:
- Build a dedicated deployment dashboard: rejected because it is outside the feature scope and adds unnecessary complexity.
- Require manual narrative reports without structured checks: rejected because operators need deterministic evidence and pass/fail status for each verification step.

## Dependencies and Integration Patterns

- Dependency: Existing startup validation from FND-004.
  - Pattern: Reuse readiness behavior so hosted verification fails clearly when runtime configuration or secret injection is incomplete.
- Dependency: Existing operational endpoints and observability from FND-005.
  - Pattern: Treat `/healthz` and `/readyz` as the first hosted checks before any MCP validation is attempted.
- Dependency: Existing baseline server tools from FND-003.
  - Pattern: Use current baseline tool discovery and one baseline invocation as the minimum hosted MCP proof.
- Integration target: Hosted platform deployment and traffic routing.
  - Pattern: Record revision identity, endpoint under test, and pass/fail results for each verification stage to keep deployment review deterministic.

## Red-Green-Refactor Plan

### Red
- Add failing contract coverage for the documented hosted verification flow and required deployment evidence fields.
- Add failing integration coverage for deployment configuration packaging and for any helper code that assembles hosted verification requests.
- Add failing documentation validation checks that require the deployment workflow to declare required inputs, revision settings, and rollback/remediation guidance.

### Green
- Add the minimum deployment packaging and documentation needed to produce a hosted revision.
- Add the minimum hosted verification helpers and examples needed to exercise liveness, readiness, initialize, list-tools, and one baseline tool invocation.
- Capture revision identity and per-check pass/fail evidence in the deployment workflow.

### Refactor
- Consolidate duplicated deployment variables and hosted verification steps into shared documentation or helper utilities.
- Remove unnecessary deployment-specific branching that does not improve operator clarity.
- Re-run full regression coverage and re-validate hosted verification documentation after cleanup.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. The technical planning decisions for
FND-006 are resolved within the current repository context and project
constitution.
