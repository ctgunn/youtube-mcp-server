# Implementation Plan: YT-108 Layer 1 Endpoint `captions.delete`

**Branch**: `108-captions-delete` | **Date**: 2026-04-08 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md)
**Input**: Feature specification from `/specs/108-captions-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `captions.delete` by extending the existing YT-101 and YT-102 integration foundation with a concrete delete contract for caption-track removal. The plan keeps the feature internal-only, models `captions.delete` as an OAuth-required destructive endpoint with explicit ownership and delegation notes, and focuses implementation on visible quota metadata, deterministic request-boundary validation, unambiguous delete outcomes, and clear distinction between access-related and target-not-found failures.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses and enums, existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`, pytest, Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation, and execution state remain in-memory and feature design artifacts remain file-based  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `captions.delete` authorization, ownership constraints, delegation behavior, and quota impact reviewable in under 1 minute before reuse  
**Constraints**: No new public MCP tools in this slice, no breaking changes to MCP transport or hosted runtime behavior, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, keep secrets and ownership credentials out of docs and logs, and keep the feature scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `captions.delete` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for follow-on caption-management work

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

- YT-108 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later caption-management work.
- Full repository verification before completion will use `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and `ruff check .`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, supported request inputs, auth expectations, quota cost, ownership and delegation requirements, delete-result behavior, and failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/108-captions-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-captions-delete-wrapper-contract.md
│   └── layer1-captions-delete-auth-contract.md
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
│   ├── test_layer1_captions_contract.py
│   ├── test_layer1_consumer_contract.py
│   └── test_layer1_metadata_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the repository's `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-108 stays internal-only and builds directly on the YT-101 executor and YT-102 metadata standards rather than introducing a new integration package or public service surface.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `captions.delete` request shape for one caption-track deletion and how unsupported fields should be rejected.
- Decide how to model OAuth-required access, ownership-sensitive behavior, and optional content-owner delegation so later layers can reuse the wrapper safely.
- Decide how to make the `50`-unit quota cost and destructive-delete expectations visible enough for downstream reuse decisions.
- Decide which current modules and tests provide the minimum-change implementation seam for an endpoint-specific caption-delete wrapper.
- Decide what contract artifacts later caption-management features should rely on when reusing `captions.delete`.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the YT-108 spec against the current Layer 1 foundation to make the missing endpoint-specific behavior explicit, especially OAuth-only guidance, ownership visibility, delete-result handling, access-versus-not-found failure handling, delegation notes, and quota visibility.
- **Green**: Resolve the request-shape, auth-mode, ownership, delegation, failure-boundary, and implementation-seam decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping decisions into one minimal strategy that extends the existing Layer 1 abstractions instead of adding a second wrapper model or a public-facing contract prematurely.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model the `captions.delete` wrapper metadata, request shape, ownership expectations, delegation guidance, and valid delete outcome needed for this endpoint-specific slice.
- Define the internal contract artifacts that future caption-management authors will use to understand the wrapper's quota behavior, supported deletion inputs, and OAuth-versus-delegation expectations.
- Provide a concrete quickstart that describes how to implement the feature in Red-Green-Refactor order while preserving the current Layer 1 execution flow and reviewability expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing design expectations for `captions.delete` metadata completeness, OAuth-required explanation, ownership visibility, delete-result clarity, and access-failure distinction before implementation tasks begin.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-auth-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/quickstart.md` with only the design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contracts, and quickstart; confirm the design still preserves internal-only scope and the existing executor-based foundation; and re-check that the design remains the smallest change that satisfies the spec.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-auth-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Delete a Caption Track Through a Typed Wrapper

- **Red**: Add failing unit and integration tests proving `captions.delete` is not yet available as a typed Layer 1 wrapper with explicit request-shape, metadata, and delete-result coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `captions.delete` metadata, validate supported caption-delete inputs, and execute through the existing shared executor path.
- **Refactor**: Consolidate wrapper naming and request-shape validation so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Understand Ownership and Delegation Preconditions Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine that `captions.delete` requires authorized access, carries ownership-sensitive behavior, or supports only a documented delegation context.
- **Green**: Implement the smallest metadata and validation changes needed to model `captions.delete` as `oauth_required` with clear maintainer-facing notes for ownership expectations, quota impact, and optional `onBehalfOfContentOwner` delegation.
- **Refactor**: Remove duplicated access, ownership, and delegation guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Review Delete-Failure Boundaries for Follow-on Work

- **Red**: Add failing contract or artifact checks proving the repository does not yet document `captions.delete` quota cost, supported delete inputs, ownership behavior, and access-versus-not-found handling clearly enough for downstream caption-management planning.
- **Green**: Implement the minimum contract-artifact and representative-test updates needed to make the wrapper reviewable for quota, auth, delete-input scope, ownership notes, delegation notes, and destructive-operation result handling.
- **Refactor**: Tighten contract language and test naming so YT-108 stays a single-endpoint Layer 1 slice rather than growing into broader caption-management tooling, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `captions.delete` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-108 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `ruff check .` before completion.
- Add regression protection for ownership-sensitive failures, delegation visibility, and the `access-denied` versus `not-found` boundary so later endpoint slices cannot silently blur destructive delete behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, OAuth tokens, ownership credentials, or deleted-resource payloads in any contract artifact, docstring, or test expectation.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `captions.delete`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
