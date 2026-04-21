# Implementation Plan: YT-123 Layer 1 Endpoint `guideCategories.list`

**Branch**: `123-guide-categories-list` | **Date**: 2026-04-21 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md)
**Input**: Feature specification from `/specs/123-guide-categories-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `guideCategories.list` by extending the existing YT-101 and YT-102 integration foundation with a concrete reference-data retrieval contract for `part` plus `regionCode` requests. The plan keeps the feature internal-only, models the endpoint as an API-key wrapper with explicit deprecated-or-unavailable lifecycle guidance, and focuses implementation on visible quota metadata, deterministic request-shape boundaries, lifecycle-aware failure handling, normalized empty-result handling, and review surfaces that make the endpoint caveat obvious before downstream reuse.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `guideCategories.list` request boundaries, lifecycle caveats, and reuse guidance reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport/runtime behavior changes outside the endpoint addition, request inputs must stay deterministic, unsupported fields must fail clearly before execution, deprecated-or-unavailable endpoint guidance must stay visible in metadata and summaries, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `guideCategories.list` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for later legacy-category and localization features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

Gate rationale:

- YT-123 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and region-lifecycle contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, `part` and `regionCode` request expectations, quota metadata, lifecycle caveat handling, normalized result interpretation, and failure boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/123-guide-categories-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-guide-categories-list-wrapper-contract.md
│   └── layer1-guide-categories-list-region-lifecycle-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    └── integrations/
        ├── __init__.py
        ├── auth.py
        ├── consumer.py
        ├── contracts.py
        ├── executor.py
        ├── youtube.py
        └── wrappers.py

tests/
├── contract/
│   ├── test_layer1_consumer_contract.py
│   ├── test_layer1_legacy_categories_contract.py
│   └── test_layer1_metadata_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-123 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary for one legacy-category endpoint.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `guideCategories.list` request shape for region-based lookup.
- Decide whether this slice should expose any optional modifiers beyond `part` and `regionCode`.
- Decide how to model the seed-required deprecated-or-unavailable platform behavior in lifecycle metadata and review surfaces.
- Decide how quota cost `1`, API-key access expectations, and lifecycle-aware failure boundaries should be represented in wrapper metadata and contract artifacts.
- Decide the smallest implementation seam and regression scope by following existing Layer 1 list-wrapper and lifecycle-note patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `guideCategories.list` endpoint-specific behavior, including request-shape validation, region lookup guidance, quota visibility, lifecycle caveat handling, and explicit distinction between validation failures, lifecycle-aware failures, and successful empty results.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping reference-data and lifecycle-note decisions into one minimal approach aligned with existing metadata patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `guideCategories.list` wrapper metadata, region lookup rules, lifecycle caveat behavior, higher-layer summary behavior, and normalized outcomes needed for this endpoint slice.
- Define contract artifacts that make request boundaries, API-key access guidance, quota visibility, and deprecated-or-unavailable endpoint behavior reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for request-shape clarity, region lookup boundaries, lifecycle caveat visibility, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-region-lifecycle-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-region-lifecycle-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Guide Categories Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `guideCategories.list` is not yet available as a typed Layer 1 wrapper with explicit region-input, metadata, and normalized retrieval coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `guideCategories.list` metadata, validate `part` plus `regionCode`, and execute through the shared executor.
- **Refactor**: Consolidate region-validation and naming patterns with existing reference-data wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand Quota and Lifecycle Caveats Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `1`, API-key access, supported region lookup inputs, and the deprecated-or-unavailable lifecycle note.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `guideCategories.list` as a deterministic internal wrapper with explicit lifecycle caveat guidance.
- **Refactor**: Remove duplicated lifecycle and reuse wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Unavailable Guide Category Lookups

- **Red**: Add failing tests proving missing required inputs, unsupported modifiers, lifecycle-aware unavailable-endpoint outcomes, and successful empty-result handling are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, lifecycle-aware unavailable, and successful retrieval boundaries for `guideCategories.list`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one legacy-category endpoint wrapper and avoid broader localization or category-surface scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `guideCategories.list` additions.
- Preserve all public MCP and hosted runtime behavior because YT-123 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, `part` plus `regionCode` guidance, lifecycle caveat visibility, higher-layer summary behavior, and normalized failure distinctions for invalid, lifecycle-aware unavailable, and empty-result paths.

### Rollback and Mitigation

- Keep the feature scoped to endpoint-specific metadata, request validation, docstrings, feature-local contracts, higher-layer retrieval summaries, and Layer 1-focused tests so rollback is a clean revert.
- Reuse existing `EndpointMetadata`, `EndpointRequestShape`, `RepresentativeEndpointWrapper`, and internal consumer abstractions so rollback does not require migrations.
- Avoid exposing secrets, API keys, or OAuth tokens in tests, docs, or logs.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

Post-design rationale:

- Design artifacts define internal Layer 1 contracts without introducing public MCP changes.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite validation commands remain `python3 -m pytest` and `ruff check .`.
- The design preserves the simplest extension path for one lifecycle-caveated reference-data wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
