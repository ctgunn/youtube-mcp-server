# Implementation Plan: YT-118 Layer 1 Endpoint `comments.update`

**Branch**: `118-comments-update` | **Date**: 2026-04-15 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md)
**Input**: Feature specification from `/specs/118-comments-update/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `comments.update` by extending the existing YT-101 and YT-102 integration foundation with a concrete OAuth-required edit contract for updating existing comment content. The plan keeps the feature internal-only, treats writable-field enforcement as the defining boundary for this slice, and focuses implementation on visible quota metadata, strict update-shape validation, clear authorization requirements, normalized updated-comment outcomes, and explicit distinction between validation failures, auth failures, immutable-field violations, and normalized upstream write failures.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `comments.update` writable-field rules, OAuth requirements, quota impact, and reuse guidance reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport/runtime behavior changes outside the endpoint addition, request shapes must stay deterministic, unsupported or malformed update payloads must fail clearly before execution, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `comments.update` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for follow-on comments and moderation features

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

- YT-118 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and auth-write contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, comment-edit rules, quota metadata, OAuth expectations, writable-field boundaries, and normalized failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/118-comments-update/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-comments-update-wrapper-contract.md
│   └── layer1-comments-update-auth-write-contract.md
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
│   ├── test_layer1_comments_contract.py
│   ├── test_layer1_consumer_contract.py
│   └── test_layer1_metadata_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-118 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `comments.update` request shape using `part` plus a writable comment `body`.
- Decide how OAuth-required behavior and writable-field guidance should be represented in wrapper metadata and contract artifacts.
- Decide how the supported writable boundary should be modeled so valid comment edits remain deterministic and immutable-field changes stay out of scope.
- Decide how quota cost `50` and writable-field expectations should be represented in wrapper metadata, docstrings, and contract artifacts.
- Decide the smallest implementation seam and regression test scope by following existing write-wrapper and comment-related patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `comments.update` endpoint-specific behavior, including writable-field validation, OAuth requirements, quota visibility, higher-layer review guidance, and normalized update-boundary rules.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping update-wrapper decisions into one minimal approach aligned with existing Layer 1 write and metadata patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `comments.update` wrapper metadata, writable-field rules, authorization behavior, higher-layer summary behavior, and normalized outcomes needed for this endpoint slice.
- Define contract artifacts that make writable-field boundaries, unsupported request shapes, quota visibility, OAuth guidance, and normalized upstream failure behavior reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for writable-field coverage, authorization clarity, invalid-update handling, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-auth-write-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-auth-write-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Update an Existing Comment Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `comments.update` is not yet available as a typed Layer 1 wrapper with explicit update-shape, metadata, and normalized updated-comment coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `comments.update` metadata, validate supported comment-edit requests, and execute through the shared executor.
- **Refactor**: Consolidate update-validation and naming patterns with existing write wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand Writable Fields and Edit Boundaries Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `50`, OAuth-required behavior, supported writable fields, and unsupported immutable-field boundaries.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `comments.update` as a deterministic internal wrapper with explicit write and writable-field notes.
- **Refactor**: Remove duplicated writable-field and auth wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Ineligible Comment-Edit Requests

- **Red**: Add failing tests proving missing edit fields, unsupported immutable-field changes, missing authorization, and normalized upstream failures are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, `auth`, immutable-field, and normalized upstream write-failure boundaries for `comments.update`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one endpoint wrapper and avoid broader comments-surface scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `comments.update` additions.
- Preserve all public MCP and hosted runtime behavior because YT-118 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, writable-field boundaries, OAuth-required behavior, and normalized failure distinctions for invalid, auth-mismatched, immutable-field, and upstream-rejected update paths.

### Rollback and Mitigation

- Keep the feature scoped to endpoint-specific metadata, update validation, docstrings, feature-local contracts, higher-layer update summaries, and Layer 1-focused tests so rollback is a clean revert.
- Reuse existing `EndpointMetadata`, `EndpointRequestShape`, `RepresentativeEndpointWrapper`, and internal consumer abstractions so rollback does not require migrations.
- Avoid exposing secrets, API keys, OAuth tokens, or comment text fixtures with sensitive data in tests, docs, or logs.

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
- The design preserves the simplest extension path for one endpoint-specific update wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
