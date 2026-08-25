# Tasks: Production Hardening

**Input**: Design documents from `/specs/402-production-hardening/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [MCP admission/cache contract](./contracts/mcp-admission-and-cache-contract.md), [operational alerting contract](./contracts/operational-alerting-contract.md), [quickstart.md](./quickstart.md)

**Tests**: Tests are mandatory. Write each Red task first and demonstrate its failure before Green work. Completion requires `make quality` after all final code changes. Every new or changed Python function requires a complete reStructuredText docstring covering purpose, arguments, return value, errors, and side effects.

**Organization**: Tasks are grouped by independently testable user story. Shared configuration and dependency injection are completed first; each story then delivers one usable increment without requiring completion of the later stories.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the internal package used by the production-hardening policies without changing public behavior.

- [X] T001 Create the hardening package entry point in `src/mcp_server/hardening/__init__.py` with a package-level reStructuredText docstring describing its internal-only scope.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide validated configuration, dependency construction, bounded common observations, and hosted deployment handoff required by every story.

**⚠️ CRITICAL**: Complete this phase before starting any user-story phase.

- [X] T002 [P] Add failing configuration/profile-validation tests for hardening defaults, invalid values, local memory mode, and hosted shared-store requirements in `tests/unit/test_production_hardening_config.py`.
- [X] T003 [P] Add failing transport-construction tests for injecting hardening dependencies without changing health, readiness, initialize, or tools/list behavior in `tests/integration/test_production_hardening_hosted_flow.py`.
- [X] T004 Implement validated rate-limit, result-cache, and alerting settings with safe defaults and profile-specific shared-store validation in `src/mcp_server/config.py`.
- [X] T005 Implement the internal hardening dependency factory and safe store-health representation in `src/mcp_server/hardening/__init__.py`.
- [X] T006 Bind validated hardening dependencies into application and transport construction in `src/mcp_server/app.py` and `src/mcp_server/transport/http.py`.
- [X] T007 Add bounded common hardening-event construction and redaction-safe aggregate hooks without caller or argument dimensions in `src/mcp_server/observability.py`.
- [X] T008 Update hosted deployment input parsing, deployment handoff, and GCP runtime environment declarations for safe hardening configuration in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, `infrastructure/gcp/main.tf`, `infrastructure/gcp/variables.tf`, `infrastructure/gcp/outputs.tf`, and `infrastructure/gcp/terraform.tfvars.example`.
- [X] T009 Add or update complete reStructuredText docstrings for every Python function changed by T004–T007 in `src/mcp_server/config.py`, `src/mcp_server/hardening/__init__.py`, `src/mcp_server/app.py`, `src/mcp_server/transport/http.py`, and `src/mcp_server/observability.py`.
- [X] T010 Refactor the shared hardening configuration and dependency wiring while keeping T002–T003 green, then run `python3 -m pytest tests/unit/test_production_hardening_config.py tests/integration/test_production_hardening_hosted_flow.py` from the repository root.

**Checkpoint**: Shared hardening dependencies are validated and injected; user-story implementation can begin.

---

## Phase 3: User Story 1 — Protect shared capacity (Priority: P1) 🎯 MVP

**Goal**: Prevent one caller from consuming shared tool capacity while returning a safe, retryable MCP response and never dispatching an over-limit call.

**Independent Test**: Initialize a hosted session, make 60 identified or 10 anonymous valid `tools/call` requests, then verify the next call returns the documented `rate_limited` MCP error and matching `Retry-After` header without reaching its dispatcher/upstream handler; a separate trusted caller remains eligible.

### Red — tests must fail before implementation

- [X] T011 [P] [US1] Add failing rolling-window boundary, retry-after, anonymous-bucket, and local-store concurrency tests in `tests/unit/test_rate_limit_policy.py`.
- [X] T012 [P] [US1] Add failing trusted-gateway/validated-credential/anonymous resolver precedence and no-raw-secret-retention tests in `tests/unit/test_hosted_security_policy.py`.
- [X] T013 [P] [US1] Add failing MCP contract tests for the `rate_limited` category, retryability, safe details, `Retry-After`, and no internal/caller-secret leakage in `tests/contract/test_production_hardening_mcp_contract.py`.
- [X] T014 [P] [US1] Add failing hosted Streamable HTTP integration tests proving rejected `tools/call` requests skip dispatcher/upstream execution while health, readiness, initialize, tools/list, denied-security, and invalid-session flows do not consume allowance in `tests/integration/test_production_hardening_hosted_flow.py`.

### Green — minimum implementation

- [X] T015 [US1] Implement the admission policy, in-memory rolling-window store, Redis-compatible atomic store, caller-class records, and fail-closed store-failure result in `src/mcp_server/hardening/rate_limit.py`.
- [X] T016 [US1] Implement trusted caller-identity resolution using only configured trusted gateway context or a non-reversible validated-credential digest in `src/mcp_server/security.py`.
- [X] T017 [US1] Add the safe protocol-native `rate_limited` error category and its bounded `retryable`/`retryAfterSeconds` details in `src/mcp_server/protocol/envelope.py` and `src/mcp_server/protocol/methods.py`.
- [X] T018 [US1] Apply admission after security, protocol, and session validation but before dispatcher execution; attach `Retry-After` while retaining existing Streamable HTTP framing in `src/mcp_server/cloud_run_entrypoint.py`.
- [X] T019 [US1] Emit bounded admission decision/decision-failure observations and ensure rejected invocations cannot be reported as dispatcher/upstream successes in `src/mcp_server/observability.py` and `src/mcp_server/transport/http.py`.
- [X] T020 [US1] Add or update complete reStructuredText docstrings for every Python function changed by T015–T019 in `src/mcp_server/hardening/rate_limit.py`, `src/mcp_server/security.py`, `src/mcp_server/protocol/envelope.py`, `src/mcp_server/protocol/methods.py`, `src/mcp_server/cloud_run_entrypoint.py`, `src/mcp_server/observability.py`, and `src/mcp_server/transport/http.py`.

### Refactor and independent validation

- [X] T021 [US1] Refactor shared admission/error/header logic without widening the public contract, then run `python3 -m pytest tests/unit/test_rate_limit_policy.py tests/unit/test_hosted_security_policy.py tests/contract/test_production_hardening_mcp_contract.py tests/integration/test_production_hardening_hosted_flow.py` from the repository root.

**Checkpoint**: User Story 1 is independently usable as the MVP.

---

## Phase 4: User Story 2 — Reuse safe read results (Priority: P2)

**Goal**: Reuse only explicitly eligible, recent public read results and expose a safe cache-status indication without serving sensitive, stale, failed, or mutated data.

**Independent Test**: Invoke an eligible `fetch` or public reference lookup twice within its policy freshness period and verify the second result is a `hit` that skips the upstream handler; verify expiry, sensitive selectors, error results, and a related successful mutation cannot reuse it.

### Red — tests must fail before implementation

- [ ] T022 [P] [US2] Add failing allowlist, selector-denylist, canonical-key, authorization-isolation, TTL, expiry, and stale-on-error tests in `tests/unit/test_result_cache_policy.py`.
- [ ] T023 [P] [US2] Add failing cache-header and preserved-success-content contract tests for `hit`, `miss`, and `bypass` in `tests/contract/test_production_hardening_mcp_contract.py`.
- [ ] T024 [P] [US2] Add failing dispatcher/hosted integration tests proving a second eligible call skips the upstream handler, an expired entry refreshes, and ineligible/error calls neither read nor write cache in `tests/integration/test_production_hardening_hosted_flow.py`.
- [ ] T025 [P] [US2] Add failing mutation-invalidation tests for playlist-item and comment/comment-thread relations, failed-mutation retention, and safe no-op invalidation in `tests/integration/test_production_hardening_observability.py`.

### Green — minimum implementation

- [ ] T026 [US2] Implement the explicit cache-policy catalog, canonical safe-key builder, in-memory/Redis-compatible result stores, TTL expiry, and relation-based invalidation in `src/mcp_server/hardening/result_cache.py`.
- [ ] T027 [US2] Wrap default dispatcher invocation with cache eligibility, complete-success storage, fresh-result behavior, and pre-success mutation invalidation in `src/mcp_server/tools/dispatcher.py`.
- [ ] T028 [US2] Attach additive `MCP-Cache-Status` response headers and expose that safe header to approved browser callers without changing MCP result content in `src/mcp_server/cloud_run_entrypoint.py` and `src/mcp_server/security.py`.
- [ ] T029 [US2] Emit bounded cache eligibility, hit, miss, expiry, invalidation, and decision-failure observations without keys, results, caller identities, or input arguments in `src/mcp_server/observability.py` and `src/mcp_server/transport/http.py`.
- [ ] T030 [US2] Add or update complete reStructuredText docstrings for every Python function changed by T026–T029 in `src/mcp_server/hardening/result_cache.py`, `src/mcp_server/tools/dispatcher.py`, `src/mcp_server/cloud_run_entrypoint.py`, `src/mcp_server/security.py`, `src/mcp_server/observability.py`, and `src/mcp_server/transport/http.py`.

### Refactor and independent validation

- [ ] T031 [US2] Refactor the cache catalog and invalidation mapping into one reviewable policy source, then run `python3 -m pytest tests/unit/test_result_cache_policy.py tests/contract/test_production_hardening_mcp_contract.py tests/integration/test_production_hardening_hosted_flow.py tests/integration/test_production_hardening_observability.py` from the repository root.

**Checkpoint**: User Story 2 is independently usable; it requires only the shared foundation and does not require alerting completion.

---

## Phase 5: User Story 3 — Respond to sustained degradation (Priority: P3)

**Goal**: Give operators deduplicated, actionable, safe alerts for sustained MCP error-rate and latency incidents, with recovery only after 15 minutes of normal observations.

**Independent Test**: Feed controlled bounded observations across the 20-request minimum and each threshold; verify one active incident per condition, no low-volume alert, a recovery state only after 15 normal minutes, and Terraform policies bound to non-production notification channels.

### Red — tests must fail before implementation

- [ ] T032 [P] [US3] Add failing rolling error-rate, p95 latency, 20-sample minimum, deduplication, missing-data, delivery-failure, and 15-minute recovery-state tests in `tests/unit/test_alert_lifecycle.py`.
- [ ] T033 [P] [US3] Add failing bounded event-classification and redaction tests for success, service, upstream, capacity, and client outcomes in `tests/integration/test_production_hardening_observability.py`.
- [ ] T034 [P] [US3] Add failing Terraform contract tests for log-metric filters, threshold values, service/environment scope, notification-channel binding, no-data behavior, and policy outputs in `tests/contract/test_production_hardening_iac_contract.py`.
- [ ] T035 [P] [US3] Add failing hosted integration tests that map safe MCP tool outcomes and latency classes to incident-state events without recording tool arguments or credentials in `tests/integration/test_production_hardening_hosted_flow.py`.

### Green — minimum implementation

- [ ] T036 [US3] Implement bounded rolling operational samples, shared alert-incident state, threshold evaluation, deduplication, delivery-state records, and delayed recovery transition in `src/mcp_server/hardening/alerting.py`.
- [ ] T037 [US3] Extend request observation with finite tool-class/outcome/cache-status fields and sanitized alert-state event emission in `src/mcp_server/observability.py`.
- [ ] T038 [US3] Classify completed public tool calls and send their bounded results to the alert evaluator without changing existing MCP success/error content in `src/mcp_server/transport/http.py` and `src/mcp_server/cloud_run_entrypoint.py`.
- [ ] T039 [US3] Create log-based eligible-volume, qualified-failure, latency/state metrics and Terraform-managed monitoring alert policies with open/close notification behavior in `infrastructure/gcp/monitoring.tf`.
- [ ] T040 [US3] Add alert enablement, thresholds, sample minimum, runbook label, operator-managed notification-channel identifiers, and exported policy/metric identifiers in `infrastructure/gcp/main.tf`, `infrastructure/gcp/variables.tf`, `infrastructure/gcp/outputs.tf`, and `infrastructure/gcp/terraform.tfvars.example`.
- [ ] T041 [US3] Document alert provisioning, non-production incident exercise, safe investigation fields, notification-channel ownership, and rollback in `infrastructure/gcp/README.md`, `docs/hosted-deployment.md`, and `README.md`.
- [ ] T042 [US3] Add or update complete reStructuredText docstrings for every Python function changed by T036–T038 in `src/mcp_server/hardening/alerting.py`, `src/mcp_server/observability.py`, `src/mcp_server/transport/http.py`, and `src/mcp_server/cloud_run_entrypoint.py`.

### Refactor and independent validation

- [ ] T043 [US3] Refactor alert condition/state serialization to keep the application and Terraform dimensions bounded and aligned, then run `python3 -m pytest tests/unit/test_alert_lifecycle.py tests/contract/test_production_hardening_iac_contract.py tests/integration/test_production_hardening_observability.py tests/integration/test_production_hardening_hosted_flow.py` and `terraform -chdir=infrastructure/gcp fmt -check` from the repository root.

**Checkpoint**: All three user stories are independently functional and their operator interface is documented.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the integrated release, documentation, infrastructure, security, and rollback posture.

- [ ] T044 [P] Review and align the production-hardening cache eligibility/invalidation documentation with the implemented policy catalog in `specs/402-production-hardening/contracts/mcp-admission-and-cache-contract.md` and `README.md`.
- [ ] T045 [P] Review and align alert thresholds, recovery timing, notification-channel ownership, and incident runbook documentation with the implemented Terraform policy in `specs/402-production-hardening/contracts/operational-alerting-contract.md`, `infrastructure/gcp/README.md`, and `docs/hosted-deployment.md`.
- [ ] T046 [P] Add regression coverage for existing health, readiness, security, session, and MCP discovery behavior under enabled hardening settings in `tests/integration/test_hosted_http_routes.py`, `tests/integration/test_hosted_mcp_security_flows.py`, and `tests/integration/test_request_observability.py`.
- [ ] T047 Validate the documented local setup, focused verification, non-production incident exercise, and rollback procedure in `specs/402-production-hardening/quickstart.md` against the implemented commands and outputs.
- [ ] T048 Run `terraform -chdir=infrastructure/gcp validate` after the required provider initialization and resolve any infrastructure validation failure in `infrastructure/gcp/monitoring.tf`, `infrastructure/gcp/main.tf`, `infrastructure/gcp/variables.tf`, or `infrastructure/gcp/outputs.tf`.
- [ ] T049 Review every touched Python module for complete reStructuredText docstrings and safe redaction in `src/mcp_server/hardening/`, `src/mcp_server/config.py`, `src/mcp_server/security.py`, `src/mcp_server/observability.py`, `src/mcp_server/transport/http.py`, `src/mcp_server/cloud_run_entrypoint.py`, `src/mcp_server/protocol/`, and `src/mcp_server/tools/dispatcher.py`.
- [ ] T050 Run `make quality` from the repository root after all final changes across `src/mcp_server/`, `tests/`, and `infrastructure/gcp/`, then fix every lint, type-check, or full-test-suite failure before marking OPS-402 complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 — Setup**: Starts immediately.
- **Phase 2 — Foundational**: Depends on T001 and blocks all user stories.
- **Phase 3 — US1 (P1)**: Depends on T010; establishes the MVP.
- **Phase 4 — US2 (P2)**: Depends on T010; does not require US1 completion, but coordinate edits to `src/mcp_server/cloud_run_entrypoint.py`, `src/mcp_server/security.py`, and `src/mcp_server/transport/http.py` if implemented concurrently.
- **Phase 5 — US3 (P3)**: Depends on T010; does not require US1 or US2 completion, but consumes the shared bounded observations from Phase 2.
- **Phase 6 — Polish**: Depends on all selected user-story phases; T050 is the final completion gate.

### User Story Completion Order

```text
Setup (T001)
  └── Foundational shared configuration and injection (T002–T010)
        ├── US1: Protect shared capacity (T011–T021)  ← MVP
        ├── US2: Reuse safe read results (T022–T031)
        └── US3: Respond to sustained degradation (T032–T043)
              └── Polish and full quality gate (T044–T050)
```

### Within Each User Story

- Complete all Red tests first and confirm they fail for the intended missing behavior.
- Complete Green implementation in the listed dependency order.
- Add/update reStructuredText docstrings before story completion.
- Complete the story Refactor task and its focused test command before moving the story to done.
- Do not consider any story or the feature complete until T050 passes.

## Parallel Execution Examples

### User Story 1

```text
Parallel Red tasks: T011, T012, T013, T014
After their interfaces are agreed: T015 and T016 can proceed in parallel.
Then sequence T017 → T018 → T019 → T020 → T021.
```

### User Story 2

```text
Parallel Red tasks: T022, T023, T024, T025
Then sequence T026 → T027 and T028 → T029 → T030 → T031.
```

### User Story 3

```text
Parallel Red tasks: T032, T033, T034, T035
After event contract agreement: T036 and T039 can proceed in parallel.
Then sequence T037 → T038 → T040 → T041 → T042 → T043.
```

## Implementation Strategy

### MVP First — User Story 1 only

1. Complete T001–T010.
2. Complete T011–T021.
3. Verify a valid over-limit hosted tool call is MCP-safe, has a retry indication, performs no dispatcher/upstream work, and leaves a distinct caller eligible.
4. Run the US1 focused suite before deciding whether to deploy or demonstrate the admission-control MVP.

### Incremental Delivery

1. Add US1 to protect capacity.
2. Add US2 to reduce repeat public-read work without changing any public result body.
3. Add US3 to make sustained error/latency behavior visible to operators.
4. Complete Phase 6 and only then accept the final production-hardening release after `make quality` passes.

### Task Format Validation

- Total tasks: 50.
- Each task starts with `- [ ]`, has a sequential `T###` identifier, includes `[P]` only where parallel work is safe, applies `[US1]`, `[US2]`, or `[US3]` to every story task, and names one or more exact repository paths.
- Story task counts: US1 = 11 (T011–T021), US2 = 10 (T022–T031), US3 = 12 (T032–T043).
