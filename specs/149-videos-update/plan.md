# Implementation Plan: YT-149 Layer 1 Endpoint `videos.update`

**Branch**: `149-videos-update` | **Date**: 2026-05-10 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/spec.md)
**Input**: Feature specification from `/specs/149-videos-update/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `videos.update` by extending the existing YT-101 and YT-102 integration foundation with a concrete video-update contract for `PUT /videos`. The plan keeps the feature internal-only, models `videos.update` as an OAuth-required update endpoint with a visible 50-unit quota cost, and focuses implementation on deterministic identifier-plus-writable-part validation, explicit writable-part guidance, clear unsupported-field boundaries, normalized updated-video result handling, and the smallest extension of the existing wrapper, transport, consumer-summary, and Layer 1 test seams.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, update execution state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `videos.update` authorization, writable-part boundaries, quota impact, and normalized update outcomes reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, require deterministic identifier-plus-update validation before execution, keep secrets and tokens out of docs and logs, keep the 50-unit quota cost visible in wrapper and review surfaces, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `videos.update` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later video-management and higher-layer update workflows

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

- YT-149 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later video-update work.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, metadata and update inputs, writable-part support, OAuth requirements, quota cost, and normalized update-result interpretation.

## Project Structure

### Documentation (this feature)

```text
specs/149-videos-update/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-videos-update-wrapper-contract.md
│   └── layer1-videos-update-auth-write-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    └── integrations/
        ├── __init__.py
        ├── consumer.py
        ├── contracts.py
        ├── executor.py
        ├── wrappers.py
        └── youtube.py

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

**Structure Decision**: Keep the feature in the existing single Python service. Limit code changes to the Layer 1 integration modules and the established unit, contract, integration, and transport test suites that already cover adjacent video list, video insert, and other update-style endpoints.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the smallest supported `videos.update` request boundary that still satisfies the feature spec and local tool inventory.
- Confirm how existing update-style wrappers expose OAuth-only behavior, quota visibility, writable-part guidance, and normalized result interpretation.
- Confirm how optional writable video fields should remain explicitly outside the promised contract unless deliberately supported.
- Confirm the minimum implementation seam for request validation, transport payload normalization, and higher-layer summary behavior.

### Research Tasks

- Review adjacent update-oriented feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/134-playlist-items-update/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/`.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` for the smallest extension seam.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` for coverage expectations.

### Phase 0 Red-Green-Refactor

- **Red**: Capture any open implementation or contract questions as explicit research topics and confirm whether any current artifact leaves `videos.update` writable boundaries, required update inputs, or failure semantics under-specified for planning.
- **Green**: Resolve each research topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/research.md` with concrete decisions on request shape, writable-part guidance, optional-field boundaries, failure separation, implementation seams, and test seams.
- **Refactor**: Remove duplicated or implementation-heavy wording from research notes so the decisions stay reviewable and directly usable by the design and tasking phases.

## Phase 1: Design and Contracts

### Design Goals

- Model `videos.update` as one deterministic internal update wrapper that requires `part` plus `body`, remains OAuth-only, and keeps the 50-unit quota cost visible.
- Keep writable behavior reviewable by documenting how the supported writable-part boundary fits within one wrapper contract rather than splitting the endpoint into multiple wrapper abstractions.
- Preserve a clear distinction between invalid request shapes, missing authorized access, normalized upstream update failures, and successful updated-video outcomes.
- Keep required input fields and unsupported optional fields visible in wrapper metadata, consumer summaries, contract artifacts, and implementation docstrings so maintainers understand the update boundary before reuse.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/contracts/layer1-videos-update-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/contracts/layer1-videos-update-auth-write-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where the current repo artifacts do not yet describe `videos.update` entities, writable-part boundaries, required identifier and update inputs, or update-result boundaries clearly enough for implementation tasking.
- **Green**: Produce the data model, wrapper contract, auth-write contract, and quickstart artifacts with enough detail to drive tests and implementation without leaking transport-specific code detail.
- **Refactor**: Remove duplicated wording across artifacts, keep the internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification and local tool inventory.

## Phase 2: Implementation Strategy

### User Story 1 - Update an Existing Video Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `videos.update` is not yet available as a typed Layer 1 wrapper with explicit identifier-plus-writable-part validation, update guidance, and normalized updated-video result coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `videos.update` metadata, validate supported update inputs, execute through the existing shared executor path, and normalize successful updated-video results.
- **Refactor**: Consolidate wrapper naming and identifier-plus-update validation so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Review Writable-Part and Authorization Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine that `videos.update` requires authorized access, carries a 50-unit quota cost, supports only the documented writable-part boundary, or exposes required update inputs clearly enough for reuse decisions.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `videos.update` as `oauth_required` with clear maintainer-facing notes for writable parts, required identifier inputs, and unsupported optional fields.
- **Refactor**: Remove duplicated quota, access, and writable-boundary guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Reject Invalid or Unauthorized Video-Update Requests Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing required identifier fields, missing writable update data, malformed writable payloads, missing OAuth access, upstream update failures, and normalized successful video updates clearly enough for downstream update planning.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, authorized-access requirements, optional-field boundaries, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-149 stays a single-endpoint Layer 1 slice rather than growing into broader video-management workflows, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `videos.update` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-149 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression protection for identifier-plus-update validation, writable-part visibility, consumer-summary reviewability, quota visibility, and the `invalid_request` versus access-related versus normalized upstream update failure versus successful updated-video boundaries so later endpoint slices cannot silently blur video-update behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, consumer summaries, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, OAuth tokens, or delegated-owner context in any contract artifact, docstring, or test expectation.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `videos.update`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
