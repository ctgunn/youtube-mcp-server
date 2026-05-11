# Implementation Plan: YT-148 Layer 1 Endpoint `videos.insert`

**Branch**: `148-videos-insert` | **Date**: 2026-05-10 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/spec.md)
**Input**: Feature specification from `/specs/148-videos-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `videos.insert` by extending the existing YT-101 and YT-102 integration foundation with a concrete video-creation contract for `POST /videos`. The plan keeps the feature internal-only, models `videos.insert` as an OAuth-required and upload-sensitive endpoint with especially visible 1600-unit quota cost, and focuses implementation on deterministic metadata-plus-upload validation, explicit standard-versus-resumable upload guidance, clear audit or private-default caveat visibility, normalized created-video result handling, and the smallest extension of the existing wrapper, transport, consumer-summary, and Layer 1 test seams.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, upload execution state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `videos.insert` authorization, upload-mode boundaries, quota impact, and audit or private-default caveats reviewable in under 3 minutes before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, require deterministic metadata-plus-upload validation before execution, keep secrets and raw upload payloads out of docs and logs, keep the 1600-unit quota cost highly visible, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `videos.insert` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later video-publishing and higher-layer creation workflows

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

- YT-148 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later video-creation work.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, metadata and upload inputs, supported upload modes, OAuth requirements, quota cost, audit or private-default caveats, and normalized creation-result interpretation.

## Project Structure

### Documentation (this feature)

```text
specs/148-videos-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-videos-insert-wrapper-contract.md
│   └── layer1-videos-insert-auth-upload-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    └── integrations/
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

**Structure Decision**: Keep the feature in the existing single Python service. Limit code changes to the Layer 1 integration modules and the established unit, contract, integration, and transport test suites that already cover adjacent upload-sensitive endpoints.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the smallest supported `videos.insert` request boundary that still satisfies the feature spec and local tool inventory.
- Confirm how existing upload-sensitive wrappers expose OAuth-only behavior, quota visibility, and upload guidance.
- Confirm how audit-related or private-default caveats should remain visible in wrapper metadata and contract artifacts without becoming a separate auth mode.
- Confirm the minimum implementation seam for request construction, result normalization, and higher-layer summary behavior.

### Research Tasks

- Review adjacent upload-oriented feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/`.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py` for the smallest extension seam.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` for coverage expectations.

### Phase 0 Red-Green-Refactor

- **Red**: Capture any open implementation or contract questions as explicit research topics and confirm whether any current artifact leaves `videos.insert` boundaries, upload modes, or audit-related caveats under-specified for planning.
- **Green**: Resolve each research topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/research.md` with concrete decisions on request shape, upload-mode guidance, quota visibility, audit or private-default caveat handling, implementation seams, and test seams.
- **Refactor**: Remove duplicated or implementation-heavy wording from research notes so the decisions stay reviewable and directly usable by the design and tasking phases.

## Phase 1: Design and Contracts

### Design Goals

- Model `videos.insert` as one deterministic internal creation wrapper that requires `part`, `body`, and `media`, remains OAuth-only, and keeps the 1600-unit quota cost highly visible.
- Keep upload behavior reviewable by documenting how standard media-upload and resumable-upload expectations fit within one wrapper contract rather than splitting the endpoint into multiple wrapper abstractions.
- Preserve a clear distinction between invalid request shapes, missing authorized access, policy-related upstream refusals, and successful video creation outcomes.
- Keep audit-related or private-default caveats visible in wrapper metadata, consumer summaries, contract artifacts, and implementation docstrings so maintainers understand the effect on initial video visibility before reuse.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-auth-upload-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where the current repo artifacts do not yet describe `videos.insert` creation entities, upload modes, audit or private-default caveats, or creation-result boundaries clearly enough for implementation tasking.
- **Green**: Produce the data model, wrapper contract, auth-upload contract, and quickstart artifacts with enough detail to drive tests and implementation without leaking transport-specific code detail.
- **Refactor**: Remove duplicated wording across artifacts, keep the internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification and local tool inventory.

## Phase 2: Implementation Strategy

### User Story 1 - Create a Video Through a Reusable Internal Upload Contract

- **Red**: Add failing unit and integration tests proving `videos.insert` is not yet available as a typed Layer 1 wrapper with explicit metadata-plus-upload validation, upload-mode guidance, and normalized created-video result coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `videos.insert` metadata, validate supported creation inputs, execute through the existing shared executor path, and normalize successful created-video results.
- **Refactor**: Consolidate wrapper naming and metadata-plus-upload validation so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Review High-Cost Upload Rules Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine that `videos.insert` requires authorized access, carries a 1600-unit quota cost, supports upload-sensitive creation, or exposes audit or private-default caveats clearly enough for reuse decisions.
- **Green**: Implement the smallest metadata, consumer-summary, and documentation changes needed to model `videos.insert` as `oauth_required` with clear maintainer-facing notes for upload modes, quota impact, and visibility caveats.
- **Refactor**: Remove duplicated quota, access, and caveat guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Reject Unsupported Upload Requests Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing required metadata, missing upload payloads, malformed upload payloads, missing OAuth access, policy-related upstream refusals, and normalized successful video creation clearly enough for downstream video-creation planning.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, authorized-access requirements, audit or private-default caveats, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-148 stays a single-endpoint Layer 1 slice rather than growing into broader video-management or publishing workflows, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `videos.insert` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-148 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression protection for metadata-plus-upload validation, quota visibility, consumer-summary reviewability, audit or private-default caveat visibility, and the `invalid_request` versus access-related versus policy-related versus normalized created-video boundaries so later endpoint slices cannot silently blur video-creation behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, consumer summaries, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, OAuth tokens, raw video-upload payloads, or delegated owner context in any contract artifact, docstring, or test expectation.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `videos.insert`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
