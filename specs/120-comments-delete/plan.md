# Implementation Plan: YT-120 Layer 1 Endpoint `comments.delete`

**Branch**: `120-comments-delete` | **Date**: 2026-04-17 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md)
**Input**: Feature specification from `/specs/120-comments-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `comments.delete` by extending the existing YT-101 and YT-102 integration foundation with a concrete OAuth-required destructive-operation contract for comment removal. The plan keeps the feature internal-only, treats deterministic delete-target validation as the defining boundary for this slice, and focuses implementation on visible quota metadata, strict comment-identifier validation, clear authorization requirements, normalized deletion-acknowledgment outcomes, and explicit distinction between validation failures, auth failures, target-state failures, and normalized upstream delete failures.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, delete execution state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `comments.delete` delete rules, OAuth requirements, quota impact, and reuse guidance reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport/runtime behavior changes outside the endpoint addition, request shapes must stay deterministic, unsupported or malformed delete payloads must fail clearly before execution, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `comments.delete` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for follow-on comment cleanup and Layer 2 work

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

- YT-120 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and auth-delete contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, delete-target rules, quota metadata, OAuth expectations, optional delegation boundaries, and normalized delete-failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/120-comments-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-comments-delete-wrapper-contract.md
│   └── layer1-comments-delete-auth-delete-contract.md
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

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-120 remains internal-only and reuses the current executor, metadata, transport, and higher-layer summary patterns rather than introducing a new abstraction boundary.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `comments.delete` request shape using one required comment identifier and only the optional delegation inputs that fit this slice cleanly.
- Decide how OAuth-required behavior and delete-target guidance should be represented in wrapper metadata and contract artifacts.
- Decide how deletion acknowledgment behavior should be modeled so valid delete requests remain deterministic and downstream layers can distinguish successful removal from invalid or unavailable-target cases.
- Decide how quota cost `50` and destructive-operation notes should be represented in wrapper metadata, docstrings, transport normalization, and contract artifacts.
- Decide the smallest implementation seam and regression test scope by following existing comment-write and delete-wrapper patterns.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `comments.delete` endpoint-specific behavior, including delete-target validation, OAuth requirements, quota visibility, deletion-acknowledgment handling, and normalized delete-boundary rules.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping delete-wrapper decisions into one minimal approach aligned with existing Layer 1 write, delete, and metadata patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `comments.delete` wrapper metadata, delete-target rules, authorization behavior, higher-layer summary behavior, and normalized acknowledgment outcomes needed for this endpoint slice.
- Define contract artifacts that make delete preconditions, unsupported request shapes, quota visibility, OAuth guidance, and normalized upstream delete failure behavior reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for delete-target coverage, authorization clarity, invalid-delete handling, and reviewability before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/layer1-comments-delete-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/layer1-comments-delete-auth-delete-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/layer1-comments-delete-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/layer1-comments-delete-auth-delete-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Delete a Comment Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `comments.delete` is not yet available as a typed Layer 1 wrapper with explicit delete-target, metadata, and normalized deletion-acknowledgment coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `comments.delete` metadata, validate supported delete requests, and execute through the shared executor.
- **Refactor**: Consolidate delete-validation and naming patterns with existing comment write and delete wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand OAuth Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express quota cost `50`, OAuth-required behavior, delete preconditions, and optional delegation boundaries.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `comments.delete` as a deterministic internal wrapper with explicit delete and authorization notes.
- **Refactor**: Remove duplicated delete and auth wording across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Ineligible Delete Requests

- **Red**: Add failing tests proving missing comment identifiers, unsupported identifier shapes, missing authorization, unavailable targets, and normalized upstream delete failures are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, `auth`, target-state, and normalized upstream delete-failure boundaries for `comments.delete`.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one endpoint wrapper and avoid broader comment-surface scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `comments.delete` additions.
- Preserve all public MCP and hosted runtime behavior because YT-120 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, delete preconditions, OAuth-required behavior, optional delegation guidance, and normalized failure distinctions for invalid, auth-mismatched, unavailable-target, and upstream-rejected delete paths.

### Rollback and Mitigation

- Keep the feature scoped to endpoint-specific metadata, delete validation, docstrings, feature-local contracts, higher-layer delete summaries, and Layer 1-focused tests so rollback is a clean revert.
- Reuse existing `EndpointMetadata`, `EndpointRequestShape`, `RepresentativeEndpointWrapper`, and internal consumer abstractions so rollback does not require migrations.
- Avoid exposing secrets, API keys, OAuth tokens, or delete fixtures with sensitive data in tests, docs, or logs.

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
- The design preserves the simplest extension path for one endpoint-specific delete wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
