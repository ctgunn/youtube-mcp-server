# Implementation Plan: YT-121 Layer 1 Endpoint `commentThreads.list`

**Branch**: `121-comment-threads-list` | **Date**: 2026-04-17 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/spec.md)
**Input**: Feature specification from `/specs/121-comment-threads-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `commentThreads.list` by extending the existing YT-101 and YT-102 integration foundation with a concrete retrieval contract for thread lookup by `videoId`, `allThreadsRelatedToChannelId`, or thread `id`. The plan keeps the feature internal-only, treats the seed-required selector paths as deterministic wrapper modes, and focuses implementation on visible quota metadata, selector exclusivity, public API-key access guidance for the supported selector set, clear request-shape boundaries, normalized empty-result handling, and explicit distinction between validation failures, access mismatches, and successful retrieval outcomes.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `commentThreads.list` selector rules, quota impact, and reuse guidance reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport/runtime behavior changes outside the endpoint addition, request selectors must stay deterministic, unsupported or conflicting selector combinations must fail clearly before execution, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `commentThreads.list` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for follow-on comment-thread features

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

- YT-121 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and lookup-auth contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, selector requirements, quota metadata, auth expectations, normalized result handling, and failure boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/121-comment-threads-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-comment-threads-list-wrapper-contract.md
│   └── layer1-comment-threads-list-lookup-auth-contract.md
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
│   ├── test_layer1_comment_threads_contract.py
│   ├── test_layer1_consumer_contract.py
│   └── test_layer1_metadata_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-121 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `commentThreads.list` request shape for thread lookup by `videoId`, `allThreadsRelatedToChannelId`, and ID-based retrieval.
- Decide whether the seed-required selector paths should be modeled as public API-key retrieval for this slice or as mixed-auth behavior immediately.
- Decide how quota cost `1` and selector-dependent request boundaries should be represented in wrapper metadata and contract artifacts.
- Decide how to preserve explicit empty-result behavior and distinct failure boundaries for missing selectors, conflicting selectors, unsupported modifiers, and access mismatches.
- Decide the smallest implementation seam and regression test scope by following existing list-wrapper and comments-related patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `commentThreads.list` endpoint-specific behavior, including selector validation, video-, channel-, and ID-based lookup guidance, quota visibility, access expectations, and explicit empty-result or invalid-request boundaries.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping retrieval-wrapper decisions into one minimal approach aligned with existing Layer 1 selector and metadata patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `commentThreads.list` wrapper metadata, selector rules, access behavior, higher-layer summary behavior, and normalized outcomes needed for this endpoint slice.
- Define contract artifacts that make lookup boundaries, selector exclusivity, quota visibility, access guidance, and empty-result behavior reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for selector coverage, video-, channel-, and ID-based lookup clarity, access guidance, empty-result behavior, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-lookup-auth-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-lookup-auth-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Comment Threads Through Supported Lookup Modes

- **Red**: Add failing unit and integration tests proving `commentThreads.list` is not yet available as a typed Layer 1 wrapper with explicit selector, metadata, and normalized retrieval coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `commentThreads.list` metadata, validate supported selectors, and execute through the shared executor.
- **Refactor**: Consolidate selector-validation and naming patterns with existing list wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand Lookup and Access Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `1`, the supported `videoId`, `allThreadsRelatedToChannelId`, and `id` retrieval paths, and the access expectation attached to each path.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `commentThreads.list` as a deterministic internal wrapper with explicit lookup and access notes.
- **Refactor**: Remove duplicated lookup and access wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Unsupported Thread Retrieval Requests

- **Red**: Add failing tests proving missing selectors, conflicting selectors, unsupported modifiers, access mismatches, and empty-result handling are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, `auth`, and successful no-match retrieval boundaries for `commentThreads.list`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one endpoint wrapper and avoid broader comment-thread surface scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `commentThreads.list` additions.
- Preserve all public MCP and hosted runtime behavior because YT-121 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, selector exclusivity, video-, channel-, and ID-based lookup guidance, higher-layer summary behavior, and normalized failure distinctions for invalid, mismatched-auth, and empty-result paths.

### Rollback and Mitigation

- Keep the feature scoped to endpoint-specific metadata, selector validation, docstrings, feature-local contracts, higher-layer retrieval summaries, and Layer 1-focused tests so rollback is a clean revert.
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
- The design preserves the simplest extension path for one endpoint-specific list wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
