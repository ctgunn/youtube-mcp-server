# Implementation Plan: YT-147 Layer 1 Endpoint `videos.list`

**Branch**: `147-videos-list` | **Date**: 2026-05-09 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md)
**Input**: Feature specification from `/specs/147-videos-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `videos.list` by extending the existing YT-101 and YT-102 integration foundation with a concrete video lookup contract that supports deterministic retrieval through `part` plus exactly one selector from `id`, `chart`, or `myRating`, while keeping collection-only refinements such as `pageToken`, `maxResults`, `regionCode`, and `videoCategoryId` bounded to the selector paths where they make sense. The plan keeps the feature internal-only, models the endpoint as a 1-unit mixed-auth wrapper with explicit selector and refinement behavior, and focuses implementation on request-shape boundaries, selector-aware auth visibility, normalized empty-result handling, and the smallest code-and-test seam needed for later Layer 2 raw tools and Layer 3 video workflows.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `videos.list` selector rules, mixed-auth expectations, quota visibility, and collection-refinement boundaries reviewable in under 2 minutes before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport or hosted runtime behavior changes outside the endpoint addition, request inputs must stay deterministic, unsupported fields must fail clearly before execution, valid empty results must stay on the success path, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `videos.list` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for later direct video lookup, chart browsing, and rating-aware video workflows

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

- YT-147 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and selector-auth behavior contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, selector rules, collection-refinement limits, quota metadata, conditional auth behavior, normalized result interpretation, and failure boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/147-videos-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-videos-list-wrapper-contract.md
│   └── layer1-videos-list-selector-auth-contract.md
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
│   ├── test_layer1_metadata_contract.py
│   └── test_layer1_videos_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-147 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary for one video-retrieval endpoint.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `videos.list` request shape spanning direct ID lookup, chart retrieval, and rating-backed retrieval.
- Decide which optional refinements remain in scope for this slice and which selectors they may accompany.
- Decide how quota cost `1`, mixed-auth expectations, selector rules, and collection-refinement boundaries should be represented in wrapper metadata and contract artifacts.
- Decide how valid empty results should be interpreted relative to invalid requests for this endpoint.
- Decide the smallest implementation seam and regression scope by following existing Layer 1 list-wrapper, consumer-summary, and transport patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `videos.list` endpoint-specific behavior, including selector validation, chart and rating refinement guidance, mixed-auth visibility, quota visibility, empty-result handling, and explicit distinction between validation failures and successful retrieval outcomes.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping selector, auth, and refinement-boundary decisions into one minimal approach aligned with existing wrapper patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `videos.list` wrapper metadata, selector rules, mixed-auth behavior, collection-refinement rules, higher-layer summary behavior, and normalized outcomes needed for this endpoint slice.
- Define contract artifacts that make request boundaries, auth guidance, quota visibility, selector behavior, and collection-refinement semantics reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for selector clarity, auth-path visibility, collection-refinement boundaries, empty-result handling, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-selector-auth-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification and local tool inventory.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-selector-auth-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Videos Through a Reusable Layer 1 Lookup Contract

- **Red**: Add failing unit and integration tests proving `videos.list` is not yet available as a typed Layer 1 wrapper with explicit selector, collection-refinement, and normalized retrieval coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `videos.list` metadata, validate `part` plus exactly one selector from `id`, `chart`, or `myRating`, honor supported optional refinements, and execute through the shared executor.
- **Refactor**: Consolidate selector-validation and naming patterns with existing list wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Review Supported Selector Modes, Auth Expectations, and Quota Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `1`, mixed-auth behavior, supported video lookup selectors, and collection-refinement rules.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `videos.list` as a deterministic internal wrapper with explicit selector and auth guidance.
- **Refactor**: Remove duplicated quota and reuse wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Reject Invalid Selector Combinations Clearly

- **Red**: Add failing tests proving missing required inputs, conflicting selectors, unsupported modifiers, unsupported chart-only refinements, and valid empty-result handling are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, successful empty-result, and successful retrieval boundaries for `videos.list`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one video-retrieval endpoint wrapper and avoid broader video-management scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `videos.list` additions.
- Preserve all public MCP and hosted runtime behavior because YT-147 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, selector rules, mixed-auth notes, collection-refinement boundaries, higher-layer summary behavior, empty-result success handling, and normalized failure distinctions for invalid versus valid lookup paths.

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
- The design preserves the simplest extension path for one video-retrieval wrapper with selector and auth guidance.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
