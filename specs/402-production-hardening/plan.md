# Implementation Plan: Production Hardening

**Branch**: `[402-production-hardening]` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/402-production-hardening/spec.md`

## Summary

Harden the hosted public MCP tool-invocation path with a shared, fail-closed per-caller admission policy; conservatively reuse only explicitly approved public read results; and emit bounded application-level operational state that Terraform-managed monitoring policies use to alert on sustained MCP failures and latency. The plan preserves existing successful tool-result shapes and Streamable HTTP behavior while adding safe error metadata and response headers for rejected or reused calls.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis client, Python standard library, Terraform Google provider  
**Storage**: Redis-compatible shared ephemeral state for hosted rate-limit windows, result-cache entries, and alert state; process-local in-memory equivalents for local development and deterministic tests; GCP logging/monitoring configuration stored as versioned Terraform files  
**Testing**: pytest, Ruff, mypy, Terraform formatting/validation, existing unit/contract/integration suites  
**Documentation Style**: Complete Python reStructuredText docstrings for every new or changed function; Markdown contracts, operator runbook, and deployment documentation  
**Target Platform**: Linux container on Cloud Run with a Redis-compatible hosted dependency; supported local development runtime  
**Project Type**: Remote MCP web service with Terraform-managed hosted infrastructure  
**Performance Goals**: Maintain 99.5% monthly availability; p95 below 3 seconds for simple/cached calls and below 8 seconds for transcript-heavy calls; reject over-limit calls before dispatcher/upstream execution  
**Constraints**: Default 60 identified and 10 anonymous valid `tools/call` invocations per rolling 60 seconds; cache freshness never exceeds 300 seconds; 10-minute alert evaluation with a 20-request minimum and 5% failure threshold; no secret, caller identity, request content, or unbounded argument value in cache keys, metrics, logs, or alerts  
**Scale/Scope**: All default public MCP tools; only an explicit, initially small allowlist of public API-key/static read operations is eligible for reuse; hosted deployment must preserve decisions across Cloud Run instances  

## Constitution Check

*GATE: Passed before Phase 0 research; re-checked and passed after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes — [admission and cache contract](./contracts/mcp-admission-and-cache-contract.md) defines non-breaking safe error/header behavior; [operational alerting contract](./contracts/operational-alerting-contract.md) defines operator-facing infrastructure behavior.
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story.
- [x] Red phase identifies failing tests before implementation tasks begin.
- [x] Green phase limits implementation to minimum code required for passing tests.
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run.
- [x] Integration and regression coverage strategy is documented.
- [x] Plan names the command that proves the full repository test suite passes before completion: `make quality`.
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions.
- [x] Observability, security, and simplicity constraints are addressed.

## Project Structure

### Documentation (this feature)

```text
specs/402-production-hardening/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── mcp-admission-and-cache-contract.md
│   └── operational-alerting-contract.md
└── tasks.md                    # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
src/mcp_server/
├── config.py                   # Validated hardening settings and profile rules
├── security.py                 # Trusted caller-identity resolution boundary
├── observability.py            # Bounded hardening measurements and alert-state events
├── protocol/
│   ├── envelope.py             # Safe rate-limited error category
│   └── methods.py              # Tool-call contract integration
├── transport/
│   ├── http.py                 # Dispatcher/runtime construction and request observations
│   └── session_store.py         # Existing separate Redis topology reference only
├── cloud_run_entrypoint.py     # Hosted request admission and safe response headers
└── hardening/
    ├── rate_limit.py           # Shared/local admission store and policy
    ├── result_cache.py         # Explicit eligibility policy, entries, and invalidation
    └── alerting.py             # Bounded rolling evaluation and recovery-held incident state

infrastructure/gcp/
├── main.tf                     # Runtime hardening configuration handoff
├── monitoring.tf               # Logging metrics and monitoring alert policies
├── variables.tf                # Safe hardening and notification-channel inputs
├── outputs.tf                  # Alert policy outputs
└── README.md                   # Provisioning, verification, and incident guidance

tests/
├── unit/
│   ├── test_production_hardening_config.py
│   ├── test_rate_limit_policy.py
│   ├── test_result_cache_policy.py
│   └── test_alert_lifecycle.py
├── contract/
│   ├── test_production_hardening_mcp_contract.py
│   └── test_production_hardening_iac_contract.py
└── integration/
    ├── test_production_hardening_hosted_flow.py
    └── test_production_hardening_observability.py
```

**Structure Decision**: Retain the existing single Python service and Terraform provider adapter. New hardening concerns are isolated in one internal package so they do not overload the session store or individual tool implementations; public behavior remains at the existing hosted `/mcp` boundary and dispatcher boundary.

## Implementation Phases and TDD Plan

### Phase 0 — Research and design decisions (complete)

- **Red**: Identify unresolved choices around multi-instance state, caller identity, public-result eligibility, MCP-compatible rejection behavior, and alert recovery semantics.
- **Green**: Record the selected shared-store, conservative-cache, and application-state-plus-platform-alert decisions in [research.md](./research.md), with no unresolved clarification markers.
- **Refactor**: Keep the design limited to three reusable policy concerns and reuse existing runtime configuration, security, observability, Redis connectivity, and Terraform conventions rather than introduce a new service or external dependency.

### Phase 1 — Contracts and operational design (complete)

- **Red**: Define failing contract assertions for rate-limited tool calls, cache status visibility, result-isolation boundaries, alert metric dimensions, Terraform notification configuration, and delayed recovery.
- **Green**: Document the state model, MCP/HTTP contract, monitoring contract, local/hosted setup, deployment inputs, and test evidence in Phase 1 artifacts.
- **Refactor**: Ensure the contracts rely on bounded classifications and existing protocol semantics; make one policy catalog the source of truth for cache eligibility and invalidation.

### Phase 2 — Implementation planning (next command: `/speckit.tasks`)

#### Shared foundation

- **Red**: Add configuration, store, and observability tests that fail for invalid hardening values, absent hosted shared state, unsafe identity input, and unbounded metric dimensions.
- **Green**: Add validated hardening settings, local and Redis-compatible policy stores, trusted-identity resolution, bounded event types, and dependency injection into the hosted transport. In staging/prod, a required shared policy-store failure returns a safe temporary-service outcome rather than bypassing protection.
- **Refactor**: Consolidate TTL, serialization, redaction, and store-health behavior across hardening components. Add or update full reStructuredText docstrings on every touched Python function.

#### User Story 1 — Protect shared capacity

- **Red**: Add exact rolling-window boundary tests (60/61 and 10/11), retry-after calculations, trusted-identity isolation, anonymous behavior, cross-instance behavior, and hosted SSE MCP rejection tests proving no dispatcher/upstream invocation occurs after rejection.
- **Green**: Apply admission after hosted security, request parsing, and session checks validate a `tools/call`, but before tool dispatch. Return the documented `rate_limited` MCP error and `Retry-After` header while retaining the existing Streamable HTTP response mechanism. Exclude health, readiness, initialize, tools/list, malformed, denied-security, and invalid-session requests from consumption.
- **Refactor**: Centralize error/header construction and preserve redaction; run focused unit/contract/integration tests, then `make quality`.

#### User Story 2 — Reuse safe read results

- **Red**: Add policy tests for every initial eligible/ineligible tool class; key canonicalization/isolation tests; hit, expiry, cache-outage, and stale-on-error tests; and mutation invalidation tests.
- **Green**: Cache only complete successful results for the explicit allowlist: static `fetch` (300 seconds), public API-key reference lookups (up to 300 seconds), `playlistItems_list` (60 seconds), and `commentThreads_list` without `moderationStatus` (30 seconds). Do not cache all mutations, uploads, downloads, ratings, moderation, OAuth, mixed/conditional, composed, `search`, or remaining baseline tools. Return `MCP-Cache-Status: hit`, `miss`, or `bypass` without changing successful MCP content.
- **Refactor**: Keep policy versioning and invalidation mapping in one catalog, rotate namespaces rather than scan broadly on policy/catalog changes, and add or update full reStructuredText docstrings for changed Python functions. Run focused tests, then `make quality`.

#### User Story 3 — Respond to sustained degradation

- **Red**: Add deterministic rolling-window tests for the 20-request minimum, 5% failure threshold, simple/cached 3-second p95, transcript-heavy 8-second p95, notification suppression, delivery-record handling, and 15-minute recovery hold. Add Terraform contract tests that fail when the log metrics, alert policies, notification-channel binding, scoped labels, or no-data behavior drift.
- **Green**: Emit sanitized, bounded operational events from the shared request boundary. Maintain shared incident state that remains active until 15 consecutive minutes of normal eligible observations, then emit a recovery state. Define Terraform logging metrics from that bounded state and provision monitoring policies that notify only on incident open and close through operator-managed verified channel identifiers.
- **Refactor**: Keep platform monitoring responsible for delivery and deduplication while application state supplies the required delayed recovery semantics. Keep contact endpoints and notification secrets out of source code, Cloud Run environment values, logs, and test fixtures. Add or update full reStructuredText docstrings for changed Python functions; run Terraform formatting/validation, focused tests, and `make quality`.

### Cross-cutting verification and rollback

- The implementation MUST preserve existing tool inputs, successful content/result shapes, security behavior, and session continuation. New safe headers/error details are additive and documented.
- Targeted evidence must include `python3 -m pytest tests/unit/test_rate_limit_policy.py tests/unit/test_result_cache_policy.py tests/unit/test_alert_lifecycle.py`, the matching contract and integration tests, `terraform -chdir=infrastructure/gcp fmt -check`, and `terraform -chdir=infrastructure/gcp validate` after required provider initialization.
- Completion evidence MUST end with `make quality`, which runs repository linting, type checking, and the full test suite after all final changes.
- Rollback disables hardening through the documented configuration only after confirming the operator impact, rolls back to the last verified deployment revision, and preserves alert policy/audit evidence. It must never delete shared state broadly or expose cached content, identities, or secret values.

## Complexity Tracking

No constitution violations or exceptions are required. Shared Redis-compatible state is justified by the existing multi-instance hosted session topology and is the smallest approach that preserves correct admission, isolation, and alert state across Cloud Run instances.
