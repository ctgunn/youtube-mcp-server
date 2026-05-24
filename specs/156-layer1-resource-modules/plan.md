# Implementation Plan: YT-156 Layer 1 Resource-Family Module Reorganization

**Branch**: `156-layer1-resource-modules` | **Date**: 2026-05-20 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Refactor the completed Layer 1 YouTube Data API integration surface into resource-family organization while preserving every established endpoint contract from YT-103 through YT-155. The plan keeps this slice internal to Layer 1, protects existing package-level and `mcp_server.integrations.wrappers` compatibility imports, introduces explicit resource-family access and response-normalizer dispatch contracts, and uses characterization tests plus existing resource-family contract suites to prove that validation, auth, quota metadata, request shapes, response shapes, and normalized failures do not change.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, urllib request tooling, and package imports; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, response-normalizer registration, compatibility exports, verification evidence, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 resource-family tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed function plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 behavior while making any supported resource family's wrapper builders, metadata, validators, and response handling discoverable by maintainers in under 2 minutes  
**Constraints**: No new public MCP tool in this slice, no hosted runtime or MCP transport behavior changes, no intentional endpoint contract changes, no duplicated shared auth/executor/retry/observability/error-normalization foundations, compatibility imports must continue to work, secrets and credentials must not appear in docs/logs/results, and every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One behavior-preserving internal refactor covering all completed Layer 1 endpoint capabilities from YT-103 through YT-155, the integration compatibility surfaces, response-normalizer selection, resource-family-focused unit/contract/integration/transport coverage, and feature-local contract documentation

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

- YT-156 does not add public MCP tools or hosted routes, so the contract gate is satisfied by documenting the internal Layer 1 compatibility contract and response-normalizer dispatch contract that later public layers depend on.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Red-Green-Refactor is required for each resource-family move: characterization tests must fail or document the missing resource-family seam first, then the minimum compatibility-preserving move is made, then duplicate transitional code is cleaned up and the full suite is rerun.
- Any new or changed Python functions, methods, module-level registry helpers, compatibility facades, or response-normalizer dispatch functions must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security and observability are addressed by preserving the existing executor, auth, credential attachment, logging hook, retry, and normalized error behavior without exposing secrets or changing request execution semantics.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-resource-family-compatibility-contract.md
│   └── layer1-response-normalizer-dispatch-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/
└── mcp_server/
    └── integrations/
        ├── __init__.py
        ├── auth.py
        ├── consumer.py
        ├── contracts.py
        ├── errors.py
        ├── executor.py
        ├── retry.py
        ├── wrappers.py
        ├── youtube.py
        └── resources/
            ├── __init__.py
            ├── activities.py
            ├── captions.py
            ├── channel_banners.py
            ├── channel_sections.py
            ├── channels.py
            ├── comment_threads.py
            ├── comments.py
            ├── guide_categories.py
            ├── localization.py
            ├── members.py
            ├── memberships_levels.py
            ├── playlist_images.py
            ├── playlist_items.py
            ├── playlists.py
            ├── search.py
            ├── subscriptions.py
            ├── thumbnails.py
            ├── video_abuse_report_reasons.py
            ├── video_categories.py
            ├── videos.py
            └── watermarks.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_layer1_activities_contract.py
│   ├── test_layer1_captions_contract.py
│   ├── test_layer1_channel_banners_contract.py
│   ├── test_layer1_channel_sections_contract.py
│   ├── test_layer1_channels_contract.py
│   ├── test_layer1_comment_threads_contract.py
│   ├── test_layer1_comments_contract.py
│   ├── test_layer1_consumer_contract.py
│   ├── test_layer1_legacy_categories_contract.py
│   ├── test_layer1_localization_contract.py
│   ├── test_layer1_members_contract.py
│   ├── test_layer1_memberships_levels_contract.py
│   ├── test_layer1_metadata_contract.py
│   ├── test_layer1_playlist_images_contract.py
│   ├── test_layer1_playlist_items_contract.py
│   ├── test_layer1_playlists_contract.py
│   ├── test_layer1_search_contract.py
│   ├── test_layer1_subscriptions_contract.py
│   ├── test_layer1_thumbnails_contract.py
│   ├── test_layer1_video_categories_contract.py
│   ├── test_layer1_videos_contract.py
│   └── test_layer1_watermarks_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Keep the feature in the existing single Python service. Add a resource-family package under the existing integration layer while keeping `wrappers.py`, `youtube.py`, and package-level exports as compatibility facades for current downstream imports.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the smallest behavior-preserving resource-family organization that satisfies the seed slice without forcing downstream callers to migrate imports.
- Confirm how wrapper classes, builder functions, metadata declarations, validators, and response normalizers can be grouped by resource family while shared foundations remain centralized.
- Confirm the compatibility import surfaces that must remain valid: `mcp_server.integrations`, `mcp_server.integrations.wrappers`, and `mcp_server.integrations.youtube`.
- Confirm the minimum explicit response-normalizer dispatch contract needed to replace a long central `operation_key` conditional chain without changing response payloads.
- Confirm which tests should characterize existing behavior before each move and which tests can be reorganized or supplemented by resource family.

### Research Tasks

- Review `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/spec.md` for the exact YT-156 scope and dependencies.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` for current concentration, compatibility surfaces, and refactor seams.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_*_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py` for existing behavior-preservation and import-compatibility coverage.
- Review recent Layer 1 artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/` for contract, data model, quickstart, TDD, and verification style.

### Phase 0 Red-Green-Refactor

- **Red**: Capture any unresolved organization, compatibility, dispatch, or testing questions as research topics and identify where current artifacts leave resource-family organization or compatibility expectations under-specified for tasking.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/research.md` with concrete decisions for module organization, compatibility facades, response-normalizer dispatch, test characterization, and docstring requirements.
- **Refactor**: Remove duplicated or implementation-heavy wording from research notes so the decisions remain directly usable by design and task generation.

## Phase 1: Design and Contracts

### Design Goals

- Model each supported YouTube resource family as a reviewable Layer 1 grouping for wrapper builders, typed wrapper classes, request-shape validators, endpoint metadata, and endpoint-specific response normalizers.
- Preserve existing behavior for every endpoint from YT-103 through YT-155, including validation, selectors, credential attachment, quota and auth metadata, response shape, and normalized upstream failure behavior.
- Keep shared Layer 1 foundations centralized and unchanged except for import paths needed to support resource-family grouping.
- Keep compatibility facades in place so existing imports from `mcp_server.integrations`, `mcp_server.integrations.wrappers`, and `mcp_server.integrations.youtube` remain valid.
- Replace the long central response-normalization branch with explicit operation-to-normalizer dispatch while preserving fallback parsing, per-operation normalizer input needs, and all current endpoint-specific payload shapes.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/layer1-resource-family-compatibility-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/layer1-response-normalizer-dispatch-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where the current repo artifacts do not yet define resource-family entities, compatibility import expectations, response-normalizer dispatch expectations, or full-inventory preservation evidence clearly enough for implementation tasking.
- **Green**: Produce the data model, compatibility contract, response-normalizer dispatch contract, and quickstart artifacts with enough detail to drive tests and implementation without adding new endpoint behavior.
- **Refactor**: Remove duplicated wording across artifacts, keep the internal-only refactor boundary explicit, and re-check that the design remains the smallest behavior-preserving change satisfying the feature specification and seed slice.

## Phase 2: Implementation Strategy

### User Story 1 - Find Resource-Family Integration Code

- **Red**: Add failing characterization tests proving representative resource families are not yet available through resource-family modules and that wrapper builders, metadata, validators, and response-handling responsibilities cannot yet be reviewed by family without broad-file traversal.
- **Green**: Move the minimum set of wrapper classes, builder functions, constants, and endpoint-specific validators for one resource family at a time into resource-family modules while keeping shared foundations imported from existing shared modules.
- **Refactor**: Remove duplicate transitional definitions after each family move, ensure new or changed functions have reStructuredText docstrings, and run focused tests for the moved family before proceeding to the next family.

### User Story 2 - Compose Stable Layer 1 Capabilities

- **Red**: Add failing compatibility tests for representative old and new access paths, including imports from `mcp_server.integrations`, `mcp_server.integrations.wrappers`, and the resource-family package.
- **Green**: Implement the smallest compatibility facades and package exports needed for old imports and new resource-family access to return the same wrapper capabilities and review surfaces.
- **Refactor**: Consolidate export lists and import boundaries to avoid circular imports, then rerun package-level compatibility tests plus representative consumer-summary tests.

### User Story 3 - Verify Behavior Preservation

- **Red**: Add or preserve failing characterization checks around endpoint contract behavior, response payload shapes, auth and quota metadata, selector validation, credential behavior, normalized upstream failure mapping, and the current response-normalizer selection behavior before replacing any broad conditional flow.
- **Green**: Implement explicit operation-to-normalizer dispatch and resource-family coverage while accommodating the current mix of normalizers that need execution context only, payload only, or both, and keep all existing unit, contract, integration, and transport expectations passing without intentional contract changes.
- **Refactor**: Tighten test names and contract documentation so the slice remains a behavior-preserving reorganization, then run targeted Layer 1 suites followed by `python3 -m pytest` and `python3 -m ruff check .`.

### Regression Strategy

- Preserve the shared Layer 1 executor, auth context, retry behavior, observability hooks, credential handling, request construction, and normalized error mapping outside the minimum changes needed for resource-family organization.
- Preserve all public MCP and hosted runtime behavior because YT-156 is internal-only.
- Re-run targeted resource-family contract tests during Red-Green-Refactor, including representative families with list-only, mutation, upload, delete, mixed-auth, OAuth-only, API-key, and conditional-selector behavior.
- Re-run `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_*_contract.py` before the final full-suite check.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep compatibility facades in `wrappers.py`, `youtube.py`, and `mcp_server.integrations.__init__` so rollback can revert individual resource-family moves without forcing downstream import changes.
- Move one resource family at a time and keep each move independently testable so a failing family can be reverted without discarding the full refactor plan.
- Avoid changing endpoint metadata values, request validation rules, response payload fields, credential sources, or normalized error categories; any accidental drift must fail characterization or contract tests.
- Avoid exposing secrets, OAuth tokens, API keys, channel-owner identity, delegated-owner credentials, or raw media payloads in docs, logs, normalized results, or tests.

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

- Feature-local contracts define the internal compatibility and normalizer-dispatch boundaries that must remain stable for downstream Layer 2 and Layer 3 work.
- No constitution exceptions are required because the design uses the existing Python service, existing shared Layer 1 foundations, and compatibility facades instead of adding a new architecture.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from characterization tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including resource-family builder exports, registry helpers, normalizer dispatch functions, and compatibility facade helpers.
- Security, observability, and simplicity are addressed by preserving existing auth, credential, logging, retry, and error-normalization behavior while making the organization easier to inspect.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
