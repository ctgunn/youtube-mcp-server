# Implementation Plan: Layer 4 Default MCP Tool-Catalog Integration Coverage

**Branch**: `403-layer4-tool-catalog` | **Date**: 2026-08-25 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/spec.md`

## Summary

Add a deterministic Layer 4 release-verification suite that obtains the default MCP catalog from the public `tools/list` route, then invokes each discovered tool through the public `tools/call` route using an explicit safe fixture. The suite will prove bidirectional fixture completeness, validate successful structured results and documented safe errors, compare returned endpoint identifiers to upstream operation metadata where applicable, and make the focused check available as `make test-tools`. This does not change the public catalog or use the credential-gated live runtime.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library; existing MCP transport, protocol router, and in-memory tool dispatcher; pytest; Make  
**Storage**: N/A — fixture definitions and per-run coverage state remain in test-process memory  
**Testing**: pytest deterministic integration suite; existing unit and contract coverage; `make test-tools`; full repository quality gate via `make quality`  
**Documentation Style**: Markdown feature contracts and README guidance; complete reStructuredText docstrings for every new or changed Python function, including test helpers  
**Target Platform**: Local and CI Python development environment; no hosted or credentialed runtime required  
**Project Type**: Remote MCP web service with an internal release-verification test layer  
**Performance Goals**: Each focused run produces exactly one individually identified result for every tool discovered at run time (77 tools in the current local default catalog) without outbound YouTube activity  
**Constraints**: Discovery must use the public route; fixture keys must exactly equal discovered names; all calls must use the public route; no credentials, network access, destructive mutation, or hard-coded catalog inventory; successful endpoint comparisons apply only when both endpoint result data and upstream operation metadata exist  
**Scale/Scope**: One test-owned fixture per default public tool; current local catalog has 77 descriptors and may grow without a plan change because discovery drives coverage

## Constitution Check

*GATE: Passed before Phase 0 research; re-checked and passed after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes — [verification contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/contracts/mcp-tool-catalog-verification-contract.md) defines the existing route envelopes and the new verification boundary; no client-visible protocol behavior changes.
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story.
- [x] Red phase identifies failing tests before implementation tasks begin.
- [x] Green phase limits implementation to the minimum fixture registry, route-level tests, Make target, and documentation required for passing tests.
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run.
- [x] Integration and regression coverage strategy is documented.
- [x] Plan names the command that proves the full repository test suite passes before completion: `make quality`.
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions.
- [x] Observability, security, and simplicity constraints are addressed — readable per-tool pytest IDs and mismatch reports are the diagnostics; fixtures contain no credentials, raw media, or real IDs; a test-owned mapping is the smallest design that catches catalog drift.

## Project Structure

### Documentation (this feature)

```text
specs/403-layer4-tool-catalog/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-tool-catalog-verification-contract.md
└── tasks.md                    # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
Makefile                                           # Add focused test-tools target
README.md                                          # Document deterministic versus live verification
tests/
└── integration/
    └── test_mcp_tool_catalog_endpoints.py         # Discovery, fixture completeness, and one public-route call per tool
```

**Structure Decision**: Keep all new executable behavior in one focused integration-test module and the existing command/documentation surfaces. The fixture registry belongs with the tests because it represents safe verification inputs, not a client-facing or runtime tool catalog. No application package, storage layer, or hosted infrastructure change is needed.

## Implementation Phases and TDD Plan

### Phase 0 — Research and design decisions (complete)

- **Red**: Identify unresolved choices for catalog authority, invocation boundary, fixture completeness, deterministic execution, and command/documentation placement.
- **Green**: Record the discovery-driven in-process route testing, explicit fixture mapping, deterministic no-runtime setup, response checks, and Make/README decisions in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/research.md).
- **Refactor**: Reuse existing transport, dispatcher, protocol, and documentation conventions rather than introduce a second registry, client, service, or external dependency.

### Phase 1 — Contracts and verification design (complete)

- **Red**: Define contract expectations that fail for route bypasses, missing/stale fixtures, duplicate fixture coverage, escaped exceptions, non-structured successes, mismatched endpoint identity, network activity, and undocumented command boundaries.
- **Green**: Document the fixture and result entities, verification contract, local workflow, safety boundary, and expected evidence in [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/data-model.md), [mcp-tool-catalog-verification-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/contracts/mcp-tool-catalog-verification-contract.md), and [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/quickstart.md).
- **Refactor**: Keep endpoint validation conditional on observable response and descriptor metadata, so baseline, retrieval, and composed tools are not assigned invented upstream expectations.

### Phase 2 — Implementation planning (next command: `/speckit.tasks`)

#### Shared verification foundation

- **Red**: Add failing integration coverage for public-route discovery; a non-empty, unique default catalog; fixture key equality in both directions; fixture argument validation; and an outbound-call guard. Include complete reStructuredText docstrings on all new test helpers.
- **Green**: Build a test-owned fixture registry keyed by public tool name and a controlled default transport with no configured YouTube runtime. Derive cases solely from the `tools/list` response, validate fixture completeness before calls, and invoke every case through `tools/call`.
- **Refactor**: Centralize JSON-RPC request construction, response classification, mismatch reporting, and safe-fixture validation without moving fixture knowledge into application code. Preserve descriptive per-tool pytest IDs and re-check docstrings.

#### User Story 1 — Verify the Default Tool Catalog

- **Red**: Add a parameterized route-invocation test that fails until every discovered tool is called through the public route and until successful responses prove non-error structured content.
- **Green**: For each discovery-derived case, submit the fixture's object arguments to `tools/call`; assert a response envelope, a non-error successful result, nonempty content, and structured content. If returned structured content exposes `endpoint` and the descriptor exposes `metadata.upstream.operationKey`, assert equality.
- **Refactor**: Keep result assertions outcome-focused rather than snapshotting full tool payloads; add complete reStructuredText docstrings for every introduced or changed Python function; run the focused suite, then `make quality`.

#### User Story 2 — Keep Tool Coverage Complete

- **Red**: Add failing cases for a discovered tool with no fixture, a stale fixture, duplicate fixture keys, invalid fixture arguments, and a success/error classification mismatch.
- **Green**: Require exactly one safe fixture for every discovered tool; reject stale or duplicate entries with the affected names. Permit deterministic no-data fixtures only when they declare the expected safe MCP error category.
- **Refactor**: Consolidate fixture completeness into one bidirectional report with stable ordering and readable failures; retain the public discovery response as the only inventory authority; run focused tests, then `make quality`.

#### User Story 3 — Operate Verification Safely

- **Red**: Add failing safety and documentation assertions for absent credentials, blocked outbound requests, non-destructive fixtures, the `test-tools` target, and the deterministic-versus-live verification explanation.
- **Green**: Add `make test-tools` for the focused suite and README instructions for it and `make test`. Make test fixtures use only safe local inputs and expected safe error categories; preserve the separately opt-in, read-only live smoke workflow.
- **Refactor**: Remove repeated command wording and ensure failure output reveals fixture/catalog drift without displaying credentials, raw media, or external identifiers. Add or update complete reStructuredText docstrings for changed Python functions; run focused tests, then `make quality`.

### Cross-cutting verification and rollback

- Focused evidence: `make test-tools` and `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_tool_catalog_endpoints.py` both pass and show one reported case per tool discovered during that run.
- Completion evidence: `make quality` passes after the final code change; it runs linting, type checking, and the full test suite. Any failure is fixed before feature completion.
- Contract evidence: test the existing `tools/list` and `tools/call` request/response shapes via the new contract rules without changing client schemas, tool names, or successful result shapes.
- Mitigation/rollback: because the feature adds only test, command, and documentation behavior, revert the feature commit or remove the focused target if it blocks delivery unexpectedly. Do not weaken or bypass the complete quality gate; preserve failure output needed to correct a fixture or catalog mismatch.

## Complexity Tracking

No constitution violations or exceptions are required. A centralized test fixture mapping is simpler and safer than generating arbitrary inputs from schemas or maintaining a second application catalog, while the public routes remain the sole source of catalog membership and invocation behavior.
