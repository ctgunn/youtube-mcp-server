# Implementation Plan: YT-119 Layer 1 Endpoint `comments.setModerationStatus`

**Branch**: `119-comments-set-moderation-status` | **Date**: 2026-04-15 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md)
**Input**: Feature specification from `/specs/119-comments-set-moderation-status/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `comments.setModerationStatus` by extending the existing YT-101 and YT-102 integration foundation with a concrete OAuth-required moderation contract for comment status changes. The plan keeps the feature internal-only, treats moderation-state enforcement as the defining boundary for this slice, and focuses implementation on visible quota metadata, strict moderation-request validation, clear authorization requirements, normalized moderation-acknowledgment outcomes, and explicit distinction between validation failures, auth failures, unsupported moderation-transition combinations, and normalized upstream moderation failures.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, moderation execution state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `comments.setModerationStatus` moderation rules, OAuth requirements, quota impact, and reuse guidance reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport/runtime behavior changes outside the endpoint addition, request shapes must stay deterministic, unsupported or malformed moderation payloads must fail clearly before execution, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `comments.setModerationStatus` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for follow-on comment moderation and Layer 2 work

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

- YT-119 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and auth-write contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, moderation-state rules, quota metadata, OAuth expectations, optional moderation-flag boundaries, and normalized failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/119-comments-set-moderation-status/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-comments-set-moderation-status-wrapper-contract.md
│   └── layer1-comments-set-moderation-status-auth-write-contract.md
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

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-119 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `comments.setModerationStatus` request shape using comment identifiers, one moderation status, and only the moderation flags that fit this slice cleanly.
- Decide how OAuth-required behavior and moderation-transition guidance should be represented in wrapper metadata and contract artifacts.
- Decide how supported moderation states and optional flag combinations should be modeled so valid moderation requests remain deterministic and unsupported combinations stay out of scope.
- Decide how quota cost `50` and moderation acknowledgment behavior should be represented in wrapper metadata, docstrings, transport normalization, and contract artifacts.
- Decide the smallest implementation seam and regression test scope by following existing write-wrapper and comment-related patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `comments.setModerationStatus` endpoint-specific behavior, including moderation-state validation, OAuth requirements, quota visibility, moderation-acknowledgment handling, and normalized moderation-boundary rules.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping moderation-wrapper decisions into one minimal approach aligned with existing Layer 1 write and metadata patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `comments.setModerationStatus` wrapper metadata, moderation-state rules, authorization behavior, optional moderation-flag boundaries, higher-layer summary behavior, and normalized acknowledgment outcomes needed for this endpoint slice.
- Define contract artifacts that make moderation-transition boundaries, unsupported request shapes, quota visibility, OAuth guidance, and normalized upstream failure behavior reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for moderation-state coverage, authorization clarity, optional moderation-flag boundaries, invalid-moderation handling, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-auth-write-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-auth-write-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Moderate Comments Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `comments.setModerationStatus` is not yet available as a typed Layer 1 wrapper with explicit moderation-shape, metadata, and normalized moderation-acknowledgment coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `comments.setModerationStatus` metadata, validate supported moderation requests, and execute through the shared executor.
- **Refactor**: Consolidate moderation-validation and naming patterns with existing write wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand Moderation-State and OAuth Boundaries Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `50`, OAuth-required behavior, supported moderation states, and optional moderation-flag boundaries.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `comments.setModerationStatus` as a deterministic internal wrapper with explicit moderation and write notes.
- **Refactor**: Remove duplicated moderation and auth wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Ineligible Moderation Requests

- **Red**: Add failing tests proving missing moderation fields, unsupported moderation transitions, incompatible optional moderation flags, missing authorization, and normalized upstream failures are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, `auth`, unsupported-transition, and normalized upstream moderation-failure boundaries for `comments.setModerationStatus`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one endpoint wrapper and avoid broader comment-surface scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `comments.setModerationStatus` additions.
- Preserve all public MCP and hosted runtime behavior because YT-119 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, moderation-transition boundaries, OAuth-required behavior, optional moderation-flag guidance, and normalized failure distinctions for invalid, auth-mismatched, unsupported-transition, and upstream-rejected moderation paths.

### Rollback and Mitigation

- Keep the feature scoped to endpoint-specific metadata, moderation validation, docstrings, feature-local contracts, higher-layer moderation summaries, and Layer 1-focused tests so rollback is a clean revert.
- Reuse existing `EndpointMetadata`, `EndpointRequestShape`, `RepresentativeEndpointWrapper`, and internal consumer abstractions so rollback does not require migrations.
- Avoid exposing secrets, API keys, OAuth tokens, or moderation fixtures with sensitive data in tests, docs, or logs.

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
- The design preserves the simplest extension path for one endpoint-specific moderation wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
