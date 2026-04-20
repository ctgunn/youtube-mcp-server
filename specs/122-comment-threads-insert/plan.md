# Implementation Plan: YT-122 Layer 1 Endpoint `commentThreads.insert`

**Branch**: `122-comment-threads-insert` | **Date**: 2026-04-19 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md)
**Input**: Feature specification from `/specs/122-comment-threads-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 write wrapper for `commentThreads.insert` by extending the existing YT-101 and YT-102 integration foundation with a concrete top-level thread-creation contract. The plan keeps the feature internal-only, models the endpoint as an OAuth-required write path with quota cost `50`, narrows the supported request shape to one deterministic video-targeted top-level comment-thread body, keeps optional `onBehalfOfContentOwner` guidance visible, and focuses implementation on clear boundaries between invalid request shapes, missing authorization, target-eligibility failures, and normalized upstream create outcomes.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `commentThreads.insert` quota impact, OAuth expectations, top-level-only boundaries, and reuse guidance reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport/runtime behavior changes outside the endpoint addition, request shapes must stay deterministic, unsupported reply-style or mixed create shapes must fail clearly before execution, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `commentThreads.insert` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for follow-on comment-thread features

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

- YT-122 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and auth-write contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, top-level create rules, quota metadata, auth expectations, normalized result handling, and failure boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/122-comment-threads-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-comment-threads-insert-wrapper-contract.md
│   └── layer1-comment-threads-insert-auth-write-contract.md
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

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-122 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `commentThreads.insert` request shape for one top-level comment-thread creation path.
- Decide whether the slice should support only top-level thread creation or broaden to reply-style or mixed create profiles.
- Decide how OAuth-required access, optional delegation guidance, and target-eligibility failures should be represented in wrapper metadata and contract artifacts.
- Decide how quota cost `50`, top-level-only boundaries, and failure distinctions should remain reviewable for maintainers and higher-layer authors.
- Decide the smallest implementation seam and regression test scope by following existing `comments.insert` and `commentThreads.list` patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `commentThreads.insert` endpoint-specific behavior, including top-level request-shape validation, quota visibility, OAuth expectations, delegation guidance, and explicit failure boundaries.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping write-wrapper decisions into one minimal approach aligned with existing Layer 1 comment-write and same-resource contract patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `commentThreads.insert` wrapper metadata, video-targeted top-level create rules, auth behavior, higher-layer summary behavior, and normalized outcomes needed for this endpoint slice.
- Define contract artifacts that make request boundaries, quota visibility, OAuth guidance, delegation expectations, and target-eligibility handling reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for top-level-only shape clarity, OAuth-required behavior, delegation guidance, target-eligibility handling, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-auth-write-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-auth-write-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Create a Top-Level Comment Thread Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `commentThreads.insert` is not yet available as a typed Layer 1 wrapper with explicit top-level create, metadata, and normalized creation coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `commentThreads.insert` metadata, validate one supported top-level create shape, and execute through the shared executor.
- **Refactor**: Consolidate create-shape validation and naming patterns with existing write wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand Top-Level Comment and OAuth Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `50`, OAuth-required behavior, top-level-only boundaries, supported create inputs, and optional delegation guidance.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `commentThreads.insert` as a deterministic internal wrapper with explicit auth and top-level-create notes.
- **Refactor**: Remove duplicated top-level-create and auth wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Ineligible Thread-Creation Requests

- **Red**: Add failing tests proving missing create inputs, unsupported reply-style or mixed shapes, missing authorization, and target-eligibility failures are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, `auth`, target-eligibility, and normalized upstream create boundaries for `commentThreads.insert`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one endpoint wrapper and avoid broader comment-thread surface scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `commentThreads.insert` additions.
- Preserve all public MCP and hosted runtime behavior because YT-122 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, top-level-only guidance, supported create-input boundaries, optional `onBehalfOfContentOwner` guidance, higher-layer summary behavior, and normalized failure distinctions for invalid, mismatched-auth, target-ineligible, and upstream-failure paths.

### Rollback and Mitigation

- Keep the feature scoped to endpoint-specific metadata, create-shape validation, docstrings, feature-local contracts, higher-layer creation summaries, and Layer 1-focused tests so rollback is a clean revert.
- Reuse existing `EndpointMetadata`, `EndpointRequestShape`, `RepresentativeEndpointWrapper`, and internal consumer abstractions so rollback does not require migrations.
- Avoid exposing secrets, API keys, OAuth tokens, or owner-partner values in tests, docs, or logs.

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
- The design preserves the simplest extension path for one endpoint-specific write wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
