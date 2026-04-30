# Implementation Plan: YT-132 Layer 1 Endpoint `playlistItems.list`

**Branch**: `132-playlist-items-list` | **Date**: 2026-04-28 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md)
**Input**: Feature specification from `/specs/132-playlist-items-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `playlistItems.list` by extending the existing YT-101 and YT-102 integration foundation with a concrete playlist-item retrieval contract. The plan keeps the feature internal-only, models the endpoint as a selector-based `GET /playlistItems` wrapper with required `part`, exactly one supported selector from `playlistId` or `id`, selector-aware paging rules, reviewable quota and API-key metadata, and normalized empty-result versus invalid-request versus access-failure boundaries for later playlist features.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `playlistItems.list` request boundaries, selector-specific paging rules, quota visibility, and API-key access expectations reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport or hosted runtime behavior changes outside the endpoint addition, exactly one supported selector per request, unsupported fields must fail clearly before execution, valid empty results must stay on the success path, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `playlistItems.list` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for later playlist-item features

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

- YT-132 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and selector-mode contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, required `part`, selector rules, paging behavior, API-key access expectations, quota metadata, normalized result handling, and failure boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/132-playlist-items-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-playlist-items-list-wrapper-contract.md
│   └── layer1-playlist-items-list-selector-modes-contract.md
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
        ├── retry.py
        ├── wrappers.py
        └── youtube.py

tests/
├── contract/
│   ├── test_layer1_consumer_contract.py
│   ├── test_layer1_metadata_contract.py
│   └── test_layer1_playlist_items_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-132 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary for one playlist-item list endpoint.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the supported `playlistItems.list` request shape, including required selectors and any selector-specific paging support.
- Decide whether `playlistItems.list` should be treated as API-key, OAuth-required, or mixed access for the seed-required selector set.
- Decide how quota cost `1`, API-key access expectations, selector rules, and paging boundaries should be represented in wrapper metadata and contract artifacts.
- Decide how valid empty results should be interpreted relative to invalid requests and access-related failures for this endpoint.
- Decide the smallest implementation seam and regression scope by following existing Layer 1 list-wrapper patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `playlistItems.list` endpoint-specific behavior, including selector validation, selector-specific paging rules, API-key enforcement, quota visibility, and explicit distinction between validation failures, access failures, and successful retrieval outcomes.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping selector, paging, and review-surface decisions into one minimal approach aligned with existing wrapper patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `playlistItems.list` wrapper metadata, selector behavior, paging rules, higher-layer summary behavior, and normalized outcomes needed for this endpoint slice.
- Define contract artifacts that make request boundaries, quota visibility, API-key access expectations, selector-specific paging behavior, and unsupported-request boundaries reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for selector clarity, paging boundaries, API-key requirements, unsupported modifier handling, empty-result interpretation, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/contracts/layer1-playlist-items-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/contracts/layer1-playlist-items-list-selector-modes-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/contracts/layer1-playlist-items-list-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/contracts/layer1-playlist-items-list-selector-modes-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Playlist Items Through Supported Lookup Modes

- **Red**: Add failing unit and integration tests proving `playlistItems.list` is not yet available as a typed Layer 1 wrapper with explicit selector, paging, metadata, and normalized retrieval coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `playlistItems.list` metadata, validate required `part` plus one supported selector, and execute through the shared executor.
- **Refactor**: Consolidate selector-aware list-validation and naming patterns with existing wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand Selector, Paging, and Access Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `1`, API-key access expectations, supported selectors, and selector-specific paging behavior.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `playlistItems.list` as a deterministic internal wrapper with explicit selector and paging guidance.
- **Refactor**: Remove duplicated access and selector-mode wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Unsupported Playlist Item Requests

- **Red**: Add failing tests proving missing required selectors, conflicting selector combinations, unsupported paging on selector modes that do not allow it, incompatible auth-mode usage, and empty-result handling are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, access-related failure, and successful no-playlist-item-result boundaries for `playlistItems.list`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one playlist-item endpoint wrapper and avoid broader playlist-item surface scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `playlistItems.list` additions.
- Preserve all public MCP and hosted runtime behavior because YT-132 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression coverage to lock quota visibility, required selector guidance, API-key behavior, selector-specific paging rules, higher-layer summary behavior, empty-result success handling, and normalized failure distinctions for invalid versus access-related paths.

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
- Full-suite validation commands remain `python3 -m pytest` and `python3 -m ruff check .`.
- The design preserves the simplest extension path for one API-key playlist-item list wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
