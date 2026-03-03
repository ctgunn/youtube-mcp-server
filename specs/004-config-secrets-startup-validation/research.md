# Research: Config + Secrets + Startup Validation (FND-004)

## Phase 0 Research Summary

### Decision: Centralize all required runtime config validation in one startup validation boundary
Rationale: A single validation boundary enforces fail-fast behavior consistently and prevents drift between app entrypoints, tool execution, and readiness checks.
Alternatives considered:
- Validate config ad hoc in each runtime component: rejected because it creates inconsistent behavior and late runtime failures.
- Rely on default values for all missing config: rejected because this hides deployment misconfiguration and violates fail-fast requirements.

### Decision: Use explicit profile rules for `dev`, `staging`, and `prod` with strict profile validation
Rationale: Deterministic environment behavior is required by the spec and reduces surprises between local and deployed environments.
Alternatives considered:
- Permit arbitrary profile strings with partial fallback logic: rejected because behavior becomes ambiguous and hard to test.
- Support only `dev` and `prod`: rejected because the PRD and feature spec require `staging` as a first-class profile.

### Decision: Distinguish non-secret required config from secret-backed required config in the contract
Rationale: The feature must enforce secure injection requirements while keeping startup errors actionable and non-sensitive.
Alternatives considered:
- Treat all config identically in error output: rejected because secret values and handling rules require stricter safety guarantees.
- Defer secret-backed requirements to later phases: rejected because FND-004 explicitly includes secret-loading contract and startup validation.

### Decision: Make readiness depend on validated config/secret state and return non-sensitive diagnostics
Rationale: Readiness is the traffic gate for Cloud Run and must accurately represent whether instances are safe to receive requests.
Alternatives considered:
- Keep readiness always healthy once process starts: rejected because it can route traffic to broken instances.
- Return full validation internals in readiness errors: rejected because it risks leaking sensitive operational details.

### Decision: Enforce Red-Green-Refactor with explicit startup/readiness test ordering
Rationale: Constitution principle III requires failing tests first, minimal pass implementation second, and behavior-preserving cleanup third.
Alternatives considered:
- Implement validation logic before tests: rejected because it violates constitution-mandated TDD.
- Rely on unit tests only: rejected because integration/contract behavior for startup/readiness must also be validated.

## Dependencies and Integration Patterns

- Dependency: FND-001 transport and method routing foundations.
  - Pattern: keep protocol routing stable; add config-readiness behavior without changing MCP method semantics.
- Dependency: FND-002 dispatcher lifecycle.
  - Pattern: ensure dispatcher/tool initialization depends on validated runtime config and profile state.
- Dependency: FND-003 baseline operational tools.
  - Pattern: ensure baseline tool availability remains intact when startup validation passes, and startup fails before tool exposure when validation fails.
- Integration target: Cloud Run health/readiness operations from PRD.
  - Pattern: readiness endpoint behavior reflects config/secret validity using non-sensitive diagnostic data.

## Red-Green-Refactor Plan

### Red
- Add failing unit tests for missing, blank, malformed, and unsupported-profile config values.
- Add failing integration tests showing startup refusal on invalid config and successful startup on valid config.
- Add failing contract tests asserting readiness is not-ready when config/secret validation fails.
- Add failing tests asserting no secret values appear in error payloads or logs.

### Green
- Implement centralized config model and validation rules for required and secret-backed settings.
- Enforce strict `dev/staging/prod` profile validation and deterministic profile requirements.
- Implement readiness state calculation from validation outcomes.
- Implement non-sensitive error mapping for startup/readiness validation failures.

### Refactor
- Consolidate repeated validation helpers and profile requirement mapping.
- Normalize validation error message formatting to one shared utility.
- Re-run full regression suite after cleanup to verify no behavior regression.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. Technical context and design decisions are resolved for planning.
