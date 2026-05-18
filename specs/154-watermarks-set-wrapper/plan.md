# Implementation Plan: YT-154 Layer 1 Endpoint `watermarks.set`

**Branch**: `154-watermarks-set-wrapper` | **Date**: 2026-05-17 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the endpoint-specific Layer 1 wrapper for `watermarks.set` by extending the existing YT-101 and YT-102 integration foundation with a concrete OAuth-required media-upload mutation contract for `POST /upload/youtube/v3/watermarks/set`. The plan keeps the feature internal-only, models `watermarks.set` with a required `channelId`, required watermark resource metadata, required `media` upload payload, visible 50-unit quota cost, optional partner-only delegation guidance, and normalized `204 No Content` success acknowledgement semantics.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, upload execution state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `watermarks.set` authorization, channel targeting, watermark metadata, media-upload limits, quota impact, and acknowledgement behavior reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, `RepresentativeEndpointWrapper`, and media-upload validation patterns, require deterministic channel/metadata/upload validation before execution, keep secrets and tokens out of docs/logs/results, keep the 50-unit quota cost visible in wrapper and review surfaces, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `watermarks.set` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later branding and channel-management workflows

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

- YT-154 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later watermark and channel-branding work.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, metadata inputs, required `channelId`, watermark resource metadata, media-upload inputs, OAuth requirements, quota cost, upload limits, `204 No Content` acknowledgement handling, and normalized failure interpretation.
- Security is addressed by requiring OAuth-only access, excluding tokens and credentials from docs/logs/results, preserving authorization failure boundaries, and keeping partner-only `onBehalfOfContentOwner` behavior explicit in the contract rather than implicit.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-watermarks-set-wrapper-contract.md
│   └── layer1-watermarks-set-auth-upload-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/
└── mcp_server/
    └── integrations/
        ├── __init__.py
        ├── consumer.py
        ├── contracts.py
        ├── executor.py
        ├── wrappers.py
        └── youtube.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_layer1_consumer_contract.py
│   ├── test_layer1_metadata_contract.py
│   └── test_layer1_watermarks_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Keep the feature in the existing single Python service. Limit code changes to the Layer 1 integration modules and the established unit, contract, integration, and transport test suites that already cover adjacent upload and mutation slices such as `thumbnails.set`, `channelBanners.insert`, and `videos.delete`.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the smallest supported `watermarks.set` request boundary that satisfies the feature spec, official documentation, and local tool inventory.
- Confirm how existing media-upload and mutation wrappers expose OAuth-only behavior, quota visibility, upload limits, request metadata, and acknowledgement semantics for maintainers.
- Confirm whether partner-only `onBehalfOfContentOwner` should be promised in this slice or documented as outside the guaranteed boundary.
- Confirm the minimum implementation seam for channel validation, watermark resource validation, upload payload validation, `204 No Content` success normalization, and higher-layer summary behavior.

### Research Tasks

- Review official Google documentation for `watermarks.set` to confirm quota cost, authorization scopes, required `channelId`, optional partner-only query parameter, media MIME types, maximum upload size, request body expectations, `204 No Content` success handling, and error boundaries.
- Review adjacent upload feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/`.
- Review mutation and acknowledgement feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/` and related video mutation slices for normalized success and failure-boundary patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` for the smallest extension seam.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and a new `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py` for coverage expectations.

### Phase 0 Red-Green-Refactor

- **Red**: Capture any open implementation or contract questions as explicit research topics and confirm whether any current artifact leaves `watermarks.set` channel input, watermark resource metadata, media-upload constraints, OAuth expectations, `204 No Content` acknowledgement, delegated partner context, or failure semantics under-specified for planning.
- **Green**: Resolve each research topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/research.md` with concrete decisions on request shape, media limits, optional delegation scope, failure separation, implementation seams, and test seams.
- **Refactor**: Remove duplicated or implementation-heavy wording from research notes so the decisions stay reviewable and directly usable by the design and tasking phases.

## Phase 1: Design and Contracts

### Design Goals

- Model `watermarks.set` as one deterministic internal media-upload mutation wrapper that requires `channelId`, a supported watermark resource body, one supported `media` upload payload, OAuth-backed access, and a visible 50-unit quota cost.
- Keep successful upload behavior reviewable by documenting that successful upstream no-content responses are normalized into watermark-update acknowledgement outcomes.
- Document `onBehalfOfContentOwner` as a partner-only optional query parameter that is outside the guaranteed wrapper boundary for this slice unless the final wrapper contract explicitly chooses to support it.
- Preserve a clear distinction between invalid request shapes, missing authorized access, unsupported image media, invalid watermark dimensions or timing metadata, forbidden channel failures, upstream unavailability, and successful acknowledgement outcomes.
- Keep required input fields and unsupported optional inputs visible in wrapper metadata, consumer summaries, contract artifacts, and implementation docstrings so maintainers understand the watermark boundary before reuse.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/layer1-watermarks-set-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/layer1-watermarks-set-auth-upload-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where the current repo artifacts do not yet describe `watermarks.set` entities, required `channelId`, watermark resource fields, upload payload rules, OAuth-only access, `204 No Content` acknowledgement, or failure boundaries clearly enough for implementation tasking.
- **Green**: Produce the data model, wrapper contract, auth-upload contract, and quickstart artifacts with enough detail to drive tests and implementation without leaking transport-specific code detail beyond the required endpoint contract.
- **Refactor**: Remove duplicated wording across artifacts, keep the internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification, official endpoint contract, and local tool inventory.

## Phase 2: Implementation Strategy

### User Story 1 - Set a Channel Watermark Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `watermarks.set` is not yet available as a typed Layer 1 wrapper with explicit `channelId` validation, watermark resource validation, media-upload validation, OAuth-only access, and normalized successful acknowledgement coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `watermarks.set` metadata, validate required channel/metadata/upload inputs, execute through the existing shared executor path, and normalize a successful no-content response into a reviewable watermark-update acknowledgement.
- **Refactor**: Consolidate wrapper naming and upload mutation result shaping so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Review Quota, OAuth, and Upload Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine that `watermarks.set` requires OAuth-backed access, carries a 50-unit quota cost, requires `channelId`, requires watermark resource metadata and media upload content, applies media limits, returns success as acknowledgement, or excludes partner-only delegated query behavior from the guaranteed boundary for this slice.
- **Green**: Implement the smallest metadata, consumer-summary, docstring, and contract changes needed to model `watermarks.set` as `oauth_required` with clear maintainer-facing notes for channel targeting, upload content expectations, watermark metadata, unsupported field guidance, optional delegation guidance, and successful acknowledgement semantics.
- **Refactor**: Remove duplicated quota, access, watermark, and upload-boundary guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Reject Invalid or Under-Authorized Watermark Requests Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing or malformed `channelId`, missing watermark resource metadata, missing `media`, unsupported image format or size, missing OAuth access, forbidden channel failures, upstream unavailable failures, and successful watermark acknowledgements clearly enough for downstream branding work.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, authorized-access requirements, upload-limit behavior, `204 No Content` success handling, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-154 stays a single-endpoint Layer 1 slice rather than growing into broader channel-branding management, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, media upload helpers, and transport helpers outside the intentional `watermarks.set` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-154 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression protection for `channelId` validation, watermark metadata validation, upload payload validation, media type and maximum-size guidance, `204 No Content` acknowledgement handling, consumer-summary reviewability, quota visibility, and the `invalid_request` versus access-related versus normalized upstream refusal versus successful acknowledgement boundaries so later endpoint slices cannot silently blur `watermarks.set` behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, consumer summaries, transport shaping, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, OAuth tokens, delegated-owner context, channel-owner identity, or uploaded image bytes in any contract artifact, docstring, log expectation, normalized result, or test fixture.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `watermarks.set`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.
- No constitution exceptions are required.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
