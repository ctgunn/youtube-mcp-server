# Implementation Plan: YT-129 Layer 1 Endpoint `playlistImages.insert`

**Branch**: `129-playlist-images-insert` | **Date**: 2026-04-26 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md)
**Input**: Feature specification from `/specs/129-playlist-images-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `playlistImages.insert` by extending the existing YT-101 and YT-102 integration foundation with a concrete playlist-image creation contract. The plan keeps the feature internal-only, models `playlistImages.insert` as an OAuth-required metadata-plus-media-upload endpoint with visible quota impact and deterministic request validation, and focuses implementation on reviewable create-input guidance, normalized success versus invalid-request versus upstream-failure handling, and a minimal extension of the existing wrapper, transport, consumer-summary, and test seams.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, upload execution state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `playlistImages.insert` authorization, required create inputs, upload boundary, and quota impact reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, require deterministic metadata-plus-upload validation before execution, keep secrets and binary upload content out of docs and logs, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `playlistImages.insert` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later playlist-image work

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

- YT-129 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later playlist-image work.
- Full repository verification before completion will use `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and `ruff check .`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, supported create inputs, auth expectations, quota cost, upload requirements, normalized creation-result handling, and failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/129-playlist-images-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-playlist-images-insert-wrapper-contract.md
│   └── layer1-playlist-images-insert-auth-upload-contract.md
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
│   └── test_layer1_playlist_images_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the repository's `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-129 stays internal-only and builds directly on the YT-101 executor foundation and YT-102 metadata standards rather than introducing a new integration package, storage layer, or public service surface.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `playlistImages.insert` request shape for one playlist-image creation request and how unsupported fields should be rejected.
- Decide how to model OAuth-required access, metadata-plus-upload input requirements, and any optional create modifiers so later layers can reuse the wrapper safely.
- Decide how to make the `50`-unit quota cost and normalized create-outcome boundaries visible enough for downstream reuse decisions.
- Decide which current modules and tests provide the minimum-change implementation seam for an endpoint-specific playlist-image creation wrapper.
- Decide what contract artifacts later playlist-image features should rely on when reusing `playlistImages.insert`.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the YT-129 spec against the current Layer 1 foundation to make the missing endpoint-specific behavior explicit, especially OAuth-only guidance, metadata-plus-upload boundaries, quota visibility, and clear distinction between validation failures, authorized upstream failures, and successful creation outcomes.
- **Green**: Resolve the request-shape, auth-mode, upload-boundary, outcome-shape, implementation-seam, and contract-surface decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping decisions into one minimal strategy that extends the existing Layer 1 abstractions instead of adding a second wrapper model, new transport surface, or public-facing contract prematurely.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model the `playlistImages.insert` wrapper metadata, request shape, upload/access expectations, and valid creation outcome needed for this endpoint-specific slice.
- Define the internal contract artifacts that future playlist-image authors will use to understand the wrapper's quota behavior, supported create inputs, OAuth expectations, and invalid-request boundaries.
- Provide a concrete quickstart that describes how to implement the feature in Red-Green-Refactor order while preserving the current Layer 1 execution flow and reviewability expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing design expectations for `playlistImages.insert` metadata completeness, OAuth-required explanation, create-input visibility, and failure-boundary clarity before implementation tasks begin.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/contracts/layer1-playlist-images-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/contracts/layer1-playlist-images-insert-auth-upload-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/quickstart.md` with only the design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contracts, and quickstart; confirm the design still preserves internal-only scope and the existing executor-based foundation; and re-check that the design remains the smallest change that satisfies the spec.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/contracts/layer1-playlist-images-insert-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/contracts/layer1-playlist-images-insert-auth-upload-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Create a Playlist Image Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `playlistImages.insert` is not yet available as a typed Layer 1 wrapper with explicit request-shape, metadata, and creation-result coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `playlistImages.insert` metadata, validate supported metadata-plus-upload inputs, and execute through the existing shared executor path.
- **Refactor**: Consolidate wrapper naming and request-shape validation so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Review Upload and Authorization Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine that `playlistImages.insert` requires authorized access, carries a required metadata-plus-upload boundary, or exposes quota impact clearly enough for reuse decisions.
- **Green**: Implement the smallest metadata and validation changes needed to model `playlistImages.insert` as `oauth_required` with clear maintainer-facing notes for create inputs, upload guidance, and quota impact.
- **Refactor**: Remove duplicated access and upload guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Reject Invalid or Unauthorized Upload Requests Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing metadata, missing media upload input, malformed upload payloads, missing OAuth access, and normalized upstream create failures clearly enough for downstream playlist-image planning.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, OAuth requirements, normalized create-result handling, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-129 stays a single-endpoint Layer 1 slice rather than growing into broader playlist-image tooling, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `playlistImages.insert` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-129 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `ruff check .` before completion.
- Add regression protection for metadata-plus-upload validation, quota visibility, consumer-summary reviewability, and the `invalid_request` versus access-related versus normalized upstream-failure boundaries so later endpoint slices cannot silently blur playlist-image creation behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, consumer summaries, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, OAuth tokens, or raw media-upload payloads in any contract artifact, docstring, or test expectation.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `playlistImages.insert`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
