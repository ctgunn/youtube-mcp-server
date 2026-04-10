# Implementation Plan: YT-109 Layer 1 Endpoint `channelBanners.insert`

**Branch**: `109-channel-banners-insert` | **Date**: 2026-04-08 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md)
**Input**: Feature specification from `/specs/109-channel-banners-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `channelBanners.insert` by extending the existing YT-101 and YT-102 integration foundation with a concrete banner-upload contract. The plan keeps the feature internal-only, models `channelBanners.insert` as an OAuth-required media-upload endpoint with explicit image constraints, delegation guidance, and a response URL that later channel-branding flows can pass into `channels.update`, and focuses implementation on visible quota metadata, deterministic request-boundary validation, normalized banner-upload outcomes, and clear distinction between access-related, invalid-upload, and channel-scope failures.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses and enums, existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`, pytest, Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation, upload execution state, and feature design artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `channelBanners.insert` authorization, image-upload constraints, delegation behavior, response-URL reuse, and quota impact reviewable in under 1 minute before reuse  
**Constraints**: No new public MCP tools in this slice, no breaking changes to MCP transport or hosted runtime behavior, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, keep secrets and binary image payloads out of docs and logs, model the endpoint as media-upload without a JSON request body, and keep the feature scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `channelBanners.insert` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for follow-on channel-branding work

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

- YT-109 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later channel-branding work.
- Full repository verification before completion will use `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and `ruff check .`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, supported request inputs, auth expectations, quota cost, image-upload requirements, response-URL behavior, delegation behavior, and failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/109-channel-banners-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-channel-banners-insert-wrapper-contract.md
│   └── layer1-channel-banners-insert-auth-upload-contract.md
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
│   └── test_layer1_metadata_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the repository's `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-109 stays internal-only and builds directly on the YT-101 executor and YT-102 metadata standards rather than introducing a new integration package or public service surface.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `channelBanners.insert` request shape for one banner upload and how unsupported fields should be rejected.
- Decide how to model OAuth-required access, media-upload constraints, and optional content-owner delegation so later layers can reuse the wrapper safely.
- Decide how to make the `50`-unit quota cost and response-URL handoff to later `channels.update` work visible enough for downstream reuse decisions.
- Decide which current modules and tests provide the minimum-change implementation seam for an endpoint-specific banner-upload wrapper.
- Decide what contract artifacts later channel-branding features should rely on when reusing `channelBanners.insert`.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the YT-109 spec against the current Layer 1 foundation to make the missing endpoint-specific behavior explicit, especially OAuth-only guidance, image constraint visibility, media-only request-body behavior, response-URL handling, delegation notes, and quota visibility.
- **Green**: Resolve the request-shape, auth-mode, upload-constraint, response-result, delegation, failure-boundary, and implementation-seam decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping decisions into one minimal strategy that extends the existing Layer 1 abstractions instead of adding a second wrapper model, transport surface, or public-facing contract prematurely.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model the `channelBanners.insert` wrapper metadata, request shape, upload constraints, delegation guidance, and valid banner-upload outcome needed for this endpoint-specific slice.
- Define the internal contract artifacts that future channel-branding authors will use to understand the wrapper's quota behavior, supported upload inputs, OAuth-versus-delegation expectations, and response-URL handoff behavior.
- Provide a concrete quickstart that describes how to implement the feature in Red-Green-Refactor order while preserving the current Layer 1 execution flow and reviewability expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing design expectations for `channelBanners.insert` metadata completeness, OAuth-required explanation, upload-constraint visibility, response-URL reviewability, and failure-boundary clarity before implementation tasks begin.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-auth-upload-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/quickstart.md` with only the design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contracts, and quickstart; confirm the design still preserves internal-only scope and the existing executor-based foundation; and re-check that the design remains the smallest change that satisfies the spec.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-auth-upload-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Upload a Channel Banner Through a Typed Wrapper

- **Red**: Add failing unit and integration tests proving `channelBanners.insert` is not yet available as a typed Layer 1 wrapper with explicit request-shape, metadata, and banner-result coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `channelBanners.insert` metadata, validate supported banner-upload inputs, and execute through the existing shared executor path.
- **Refactor**: Consolidate wrapper naming and request-shape validation so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Understand Upload and Delegation Preconditions Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine that `channelBanners.insert` requires authorized access, carries image-upload constraints, or supports only a documented optional `onBehalfOfContentOwner` delegation context.
- **Green**: Implement the smallest metadata and validation changes needed to model `channelBanners.insert` as `oauth_required` with clear maintainer-facing notes for upload constraints, response-URL reuse, quota impact, and optional delegated content-owner behavior.
- **Refactor**: Remove duplicated access, upload, and delegation guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Review Banner-Update Readiness for Follow-on Work

- **Red**: Add failing contract or artifact checks proving the repository does not yet document `channelBanners.insert` quota cost, supported upload inputs, response-URL behavior, and access-versus-invalid-upload handling clearly enough for downstream channel-branding planning.
- **Green**: Implement the minimum contract-artifact and representative-test updates needed to make the wrapper reviewable for quota, auth, upload scope, delegation notes, response-URL semantics, and normalized upload-result handling.
- **Refactor**: Tighten contract language and test naming so YT-109 stays a single-endpoint Layer 1 slice rather than growing into broader channel-branding tooling, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `channelBanners.insert` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-109 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `ruff check .` before completion.
- Add regression protection for upload validation, optional delegation visibility, response-URL propagation, and the `auth` versus `invalid_request` versus `target_channel` boundary so later endpoint slices cannot silently blur banner-update behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, OAuth tokens, content-owner credentials, or raw image payloads in any contract artifact, docstring, or test expectation.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `channelBanners.insert`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
