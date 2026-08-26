# Implementation Plan: Layer 4 Configured-Runtime Capability and Live-Verification Matrix

**Branch**: `404-layer4-runtime-verification` | **Date**: 2026-08-26 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/spec.md`

## Summary

Add a Layer 4 verification matrix that discovers public YouTube tool families through MCP and verifies their configured API-key, OAuth-required, and unavailable-capability behavior through the public `tools/call` route. The deterministic matrix will compose the existing configured live runtime with a controlled request opener, record only credential-safe request facts, and prohibit external networking. Extend the existing opt-in local live smoke workflow with a reviewed public read-only allowlist, per-tool safe reports, bounded execution, and fail-closed preflight checks. The feature adds internal verification, command, and documentation surfaces only; it does not change client-facing tool contracts or add a remote-server smoke flow.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library; existing MCP transport and protocol router; existing configured YouTube runtime; pytest; Make  
**Storage**: N/A — matrix cases, captured request facts, allowlist entries, and reports remain in process memory  
**Testing**: pytest integration and contract coverage; `make test-tools`; new deterministic `make test-runtime`; manually authorized `make test-live-smoke`; full quality gate via `make quality`  
**Documentation Style**: Markdown feature contracts and README guidance; complete reStructuredText docstrings for every new or changed Python function, including test and script helpers  
**Target Platform**: Local and CI Python development environments; manually run live smoke against the external YouTube service only when explicitly authorized  
**Project Type**: Remote MCP web service with an internal Layer 4 release-verification layer  
**Performance Goals**: A deterministic matrix produces one individually identified result for every discovered YouTube family in the current default catalog (22 families) with zero external requests; an authorized live smoke run obeys the allowlist's bounded request count and per-request timeout  
**Constraints**: Use `tools/list` and `tools/call` through `/mcp`; derive YouTube-family coverage from public descriptor metadata; do not treat the five generic baseline/retrieval tools as configured-YouTube cases; use controlled openers and block socket/URL networking in deterministic tests; never emit API keys, OAuth material, authorization headers, raw request bodies, raw upstream response bodies, signed URLs, or secret-bearing inputs; live smoke must be explicit, API-key public-read only, allowlisted, bounded, read-only, and excluded from `make test`, `make quality`, CI, and deployment gates  
**Scale/Scope**: One or more reviewed matrix cases per discovered YouTube family (currently 22 families / 72 YouTube descriptors); a deliberately small explicit live-smoke allowlist, initially retaining only reviewed API-key public-read operations; no persistence, public schema change, or remote MCP flow

## Constitution Check

*GATE: Passed before Phase 0 research; re-checked and passed after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes — [configured-runtime verification contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/contracts/mcp-configured-runtime-verification-contract.md) documents verification of existing MCP request and result envelopes; no client-visible MCP contract changes.
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story.
- [x] Red phase identifies failing tests before implementation tasks begin.
- [x] Green phase limits implementation to the test-owned matrix, controlled request capture, allowlisted smoke workflow, focused commands, and documentation needed for passing tests.
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run.
- [x] Integration and regression coverage strategy is documented.
- [x] Plan names the command that proves the full repository test suite passes before completion: `make quality`.
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions.
- [x] Observability, security, and simplicity constraints are addressed — individually reported pytest IDs and safe per-tool summaries provide diagnostics; controlled records omit secret-bearing fields; test-owned records and one small smoke allowlist reuse the existing runtime without adding application storage or an additional service.

## Project Structure

### Documentation (this feature)

```text
specs/404-layer4-runtime-verification/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-configured-runtime-verification-contract.md
└── tasks.md                    # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
Makefile                                              # Add deterministic runtime and manual live-smoke targets
README.md                                             # Document three verification boundaries and safe commands
scripts/
└── verify_youtube_live.py                            # Extend opt-in, allowlisted, credential-safe smoke workflow
tests/
└── integration/
    ├── test_mcp_configured_runtime_matrix.py         # New public-route configured capability matrix
    ├── test_youtube_live_smoke.py                    # Gating and authorized allowlist smoke evidence
    └── test_ci_quality_gate_docs.py                  # README command-boundary regression checks
```

**Structure Decision**: Keep deterministic configured-runtime behavior in a dedicated integration-test module because its matrix records are test-owned verification inputs, not runtime tool metadata. Keep the manually invoked live boundary in the existing verification script and smoke test. Reuse application composition, the MCP transport, configured runtime, and existing redaction conventions; no new application package, persistence layer, public tool, or remote-client component is required.

## Implementation Phases and TDD Plan

### Phase 0 — Research and design decisions (complete)

- **Red**: Identify unresolved choices for configured composition, public-route coverage, generic-tool exclusion, conditional authorization selection, controlled request observation, smoke selection, redaction, execution bounds, command placement, and remote-flow boundary.
- **Green**: Record decisions in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/research.md): compose the existing app with a controlled opener; discover families through descriptor metadata; use reviewed argument selections for conditional tools; report only sanitized request facts; retain a separate explicit local live-smoke allowlist; and defer remote server verification to OPS-405.
- **Refactor**: Reuse existing `create_app`, `MCPHTTPTransport`, capability settings, MCP error mapping, test fake-response patterns, and sanitization rather than inventing a second runtime, capability registry, or remote client.

### Phase 1 — Contracts and verification design (complete)

- **Red**: Define design rules that fail for direct-dispatch bypasses, missing or stale YouTube-family cases, false representative success in configured mode, unexpected network access, secret-bearing diagnostic fields, absent smoke authorization, unapproved or mutation-capable live invocation, unbounded smoke work, and undocumented command boundaries.
- **Green**: Document matrix, request-record, coverage-report, smoke-allowlist, and verification-report entities in [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/data-model.md); document existing MCP envelope expectations and safety rules in [mcp-configured-runtime-verification-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/contracts/mcp-configured-runtime-verification-contract.md); record safe operator commands and evidence in [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/quickstart.md).
- **Refactor**: Keep matrix case facts test-owned and live-smoke eligibility explicitly maintained, not inferred from names or generic read-like metadata. Keep generic baseline/retrieval descriptors explicitly outside the configured YouTube capability matrix.

### Phase 2 — Implementation planning (next command: `/speckit.tasks`)

#### Shared verification foundation

- **Red**: Add failing tests for discovery-derived YouTube-family coverage, family-case validity, public MCP request construction, controlled opener behavior, network prohibition, redacted captured records, and safe error-envelope classification. Add complete reStructuredText docstrings to every new or changed Python helper.
- **Green**: Build a test-owned immutable capability-matrix registry and controlled response recorder in `tests/integration/test_mcp_configured_runtime_matrix.py`. Compose each configured transport through `create_app` with sentinel credentials and the controlled opener; submit `tools/list` and `tools/call` through `/mcp`; block socket and URL opening at the test boundary.
- **Refactor**: Centralize route requests, descriptor-family extraction, capability case validation, safe-record serialization, error classification, and mismatch messages. Retain public tool/family pytest IDs and re-check docstrings after cleanup.

#### User Story 1 — Verify Configured Capability Boundaries

- **Red**: Add parameterized public-route tests that fail until every discovered YouTube family has reviewed API-key, OAuth-required, or unavailable-capability matrix coverage, including deliberately selected public and owner/conditional selectors where needed.
- **Green**: Derive the covered-family set from discovery metadata (`resourceFamily` for endpoint tools and `family` for composed tools), explicitly exclude generic baseline/retrieval descriptors, and require exact no-missing/no-stale case coverage. For API-key cases, assert the configured route returns a structured MCP success and one safe controlled request record. For OAuth-absent and otherwise unavailable cases, assert the documented safe MCP error category and zero recorded external requests.
- **Refactor**: Consolidate conditional-selector and error-envelope assertions without using a hard-coded public catalog. Keep the case data readable by family and run `make test-runtime` before the complete quality gate.

#### User Story 2 — Prove the Live Runtime Boundary

- **Red**: Add tests that fail if an API-key matrix case returns representative local data, fails to construct the expected controlled request, allows real networking, produces multiple unbounded attempts, or exposes sentinel API-key/OAuth/header/body values in an MCP result, error, capture record, or assertion message.
- **Green**: Record only tool/family, path shape, HTTP method, selected credential mode, and bounded request count. Return controlled upstream responses to prove the configured live executor rather than local fixtures is used. Enforce no-network guards and assert safe MCP errors plus no capture record when configuration is missing.
- **Refactor**: Reuse the project's existing request/response fake and sanitization conventions; eliminate duplicated secret checks while preserving coverage of result, error, and diagnostic surfaces. Add or update complete reStructuredText docstrings and run focused runtime plus existing Layer 1 live-runtime regression suites.

#### User Story 3 — Run an Opt-In Read-Only Live Smoke Check

- **Red**: Add deterministic tests that fail for absent enablement flags or credentials, non-member allowlist entries, unsafe operation classes, unbounded selection or timeouts, raw exception output, non-redacted reports, and live-smoke target inclusion in ordinary test/quality paths.
- **Green**: Extend `scripts/verify_youtube_live.py` with an explicit reviewed API-key public-read allowlist, preflight checks before app construction, discovery membership validation, public MCP invocation, bounded per-run/per-request execution, per-tool safe reports, excluded-tool reporting, and fixed/classified credential-safe failure output. Extend the opt-in smoke tests and add `make test-live-smoke`; add `make test-runtime` for the deterministic matrix only.
- **Refactor**: Keep the allowlist deliberately small and explicit; remove duplicated gate and redaction logic; confirm `make test`, `make quality`, CI, and hosted deployment continue to omit live smoke. Add or update complete reStructuredText docstrings and run deterministic smoke unit/integration coverage without real credentials.

### Cross-cutting verification and rollback

- Focused deterministic evidence: `make test-tools`; `make test-runtime`; and `PYTHONPATH=src python3 -m pytest tests/integration/test_layer1_live_runtime.py` pass without real credentials or external network activity.
- Authorized manual evidence: `RUN_YOUTUBE_LIVE_SMOKE=1 YOUTUBE_API_KEY='operator-supplied-value' make test-live-smoke` runs only after operator approval. Its output contains only per-tool safe summaries; it does not form part of normal completion evidence.
- Completion evidence: `make quality` passes after the final code or documentation change; it runs linting, type checking, and the complete test suite. Any failure is fixed before completion.
- Contract evidence: deterministic tests send `tools/list` and `tools/call` through the existing MCP route and validate existing success/error envelopes, safe categories, and zero-leak diagnostic behavior without changing client schemas, tool names, or result shapes.
- Mitigation/rollback: revert the feature commit if the new verification assets unexpectedly block delivery. Do not weaken no-network guards, fail-closed smoke prerequisites, the explicit allowlist, or the complete quality gate. Correct missing/stale cases or unsafe reporting instead.

## Complexity Tracking

No constitution violations or exceptions are required. Test-owned matrix records plus the existing configured runtime are simpler than a second registry or mock server. An explicit small allowlist is safer than inferred live eligibility, while OPS-405 remains responsible for remote MCP end-to-end behavior.
