# Implementation Plan: YT-113 Layer 1 Endpoint `channelSections.insert`

**Branch**: `113-channel-sections-insert` | **Date**: 2026-04-12 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md)
**Input**: Feature specification from `/specs/113-channel-sections-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `channelSections.insert` by extending the YT-101 and YT-102 foundation with a concrete OAuth-required create contract. The plan centers on a deterministic `part` plus `body` request shape, section-type-driven content rules for playlists and channels, explicit title and delegation guidance, and clear rejection of unsupported or malformed create payloads without introducing any new public MCP tool surface.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve current Layer 1 execution behavior while making `channelSections.insert` create-shape, OAuth, quota, and section-content rules reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no transport/runtime behavior changes, section-type rules must stay deterministic, unsupported or malformed create bodies must fail clearly before execution, and secrets or credential material must not appear in logs, tests, or docs  
**Scale/Scope**: One internal `channelSections.insert` wrapper slice affecting representative integration modules, Layer 1 unit/contract/integration/transport tests, and feature-local contract documentation for follow-on channel-organization features

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

- YT-113 is internal Layer 1 work; contract requirements are satisfied by feature-local wrapper and auth-write contract artifacts.
- Full repository verification before completion will use `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions in scope must include reStructuredText docstrings covering wrapper purpose, section-type rules, auth expectations, quota metadata, delegation guidance, and normalized failure boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/113-channel-sections-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-channel-sections-insert-wrapper-contract.md
│   └── layer1-channel-sections-insert-auth-write-contract.md
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
│   ├── test_layer1_channel_sections_contract.py
│   ├── test_layer1_consumer_contract.py
│   └── test_layer1_metadata_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-113 remains internal-only and reuses the current executor and metadata standards rather than creating a new abstraction boundary.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `channelSections.insert` request shape for `part` plus channel-section `body`.
- Decide how OAuth-required behavior and optional content-owner delegation should be represented in wrapper metadata and contract artifacts.
- Decide how section-type-specific content rules should be modeled for playlist-backed and channel-backed sections.
- Decide implementation seam and regression test scope by following existing write-wrapper patterns.
- Decide how malformed create requests remain distinct from auth failures and upstream create-limit failures.

### Planned Red-Green-Refactor Flow

- **Red**: Capture what is currently missing for `channelSections.insert` endpoint-specific behavior, including write-body rules, OAuth requirements, quota visibility, and section-type guidance.
- **Green**: Resolve all planning unknowns in `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md` with concrete decisions and no unresolved clarification markers.
- **Refactor**: Consolidate overlapping research decisions into one minimal approach aligned with existing Layer 1 write-wrapper patterns and constitution constraints.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model `channelSections.insert` wrapper metadata, section-type content rules, OAuth behavior, optional delegation context, and normalized outcomes needed for this endpoint slice.
- Define contract artifacts that make create boundaries, auth expectations, quota visibility, title rules, and invalid-create handling reviewable.
- Provide a quickstart that preserves Red-Green-Refactor sequencing and full-suite verification expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Document failing design expectations for create-shape coverage, OAuth clarity, delegation guidance, and invalid section-content behavior before implementation tasks are created.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/quickstart.md` with only required design detail.
- **Refactor**: Remove duplicated wording across artifacts, keep internal-only scope explicit, and re-check that design remains the smallest change that satisfies the feature specification.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Create a Channel Section Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `channelSections.insert` is not yet available as a typed Layer 1 wrapper with explicit create-body coverage and created-section results.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to expose representative `channelSections.insert` metadata, validate section-content request inputs, enforce OAuth-required access, and execute through the shared executor.
- **Refactor**: Consolidate create-validation and naming patterns with existing wrappers, then rerun targeted Layer 1 suites followed by full repository validation.

### User Story 2 - Understand Write Preconditions Before Reuse

- **Red**: Add failing contract and integration checks proving maintainer-facing artifacts do not yet clearly express OAuth-required behavior, quota cost `50`, supported section-type rules, and title or delegation guidance.
- **Green**: Implement the smallest metadata and documentation changes needed to model `channelSections.insert` as an OAuth-required create wrapper with explicit section-type notes.
- **Refactor**: Remove duplicated auth and section-content guidance across docstrings and contracts, then rerun targeted and full repository suites.

### User Story 3 - Fail Clearly for Invalid or Ineligible Create Requests

- **Red**: Add failing tests proving missing authorization, incomplete section bodies, unsupported content combinations, duplicate item references, and invalid optional delegation context are not yet distinct enough for downstream callers.
- **Green**: Implement minimum validation and normalization updates needed to preserve distinct `invalid_request`, `auth`, and unsupported-create boundaries.
- **Refactor**: Tighten failure wording and test names to keep the slice focused on one endpoint wrapper and avoid broader channel-management scope creep.

### Regression Strategy

- Preserve existing Layer 1 executor behavior, auth context plumbing, logging hooks, and transport helpers outside intentional `channelSections.insert` additions.
- Preserve all public MCP and hosted runtime behavior because YT-113 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport suites during development, then run `python3 -m pytest` and `ruff check .` before completion.
- Add regression coverage to lock quota visibility, OAuth-required behavior, supported section-type boundaries, title and delegation guidance, and normalized failure distinctions.

### Rollback and Mitigation

- Keep the feature scoped to endpoint-specific metadata, create validation, docstrings, feature-local contracts, and Layer 1-focused tests so rollback is a clean revert.
- Reuse existing `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` abstractions so rollback does not require migrations.
- Avoid exposing secrets, OAuth tokens, or raw credential material in tests, docs, or logs.

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
- The design preserves the simplest extension path for one endpoint-specific wrapper.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
