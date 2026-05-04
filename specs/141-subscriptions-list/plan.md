# Implementation Plan: YT-141 Layer 1 Endpoint `subscriptions.list`

**Branch**: `141-subscriptions-list` | **Date**: 2026-05-04 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md)
**Input**: Feature specification from `/specs/141-subscriptions-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `subscriptions.list` by extending the existing YT-101 and YT-102 integration foundation with a concrete mixed-auth retrieval contract. The plan models selector-driven behavior across `channelId`, `id`, `mine`, `myRecentSubscribers`, and `mySubscribers`, keeps selector rules deterministic through mutually exclusive validation, preserves near-raw paging and ordering guidance where collection-style retrieval is supported, and keeps quota, OAuth boundaries, and normalized populated versus empty versus failed outcomes reviewable without introducing any new public MCP tool surface.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and subscription-list execution state remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `subscriptions.list` selector modes, OAuth requirements, paging and ordering boundaries, and empty-result handling reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, keep the official quota cost `1` visible in review surfaces, reject unsupported or incompatible selector, paging, and ordering combinations deterministically before execution where the wrapper defines them, keep secrets and tokens out of docs and logs, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `subscriptions.list` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later subscription-dependent work

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

- YT-141 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later subscription-dependent work.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, selector rules, OAuth expectations, paging and ordering boundaries, quota cost, and normalized failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/141-subscriptions-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-subscriptions-list-wrapper-contract.md
│   └── layer1-subscriptions-list-filter-modes-contract.md
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
│   ├── test_layer1_metadata_contract.py
│   ├── test_layer1_subscriptions_contract.py
│   └── test_layer1_consumer_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the repository's `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-141 stays internal-only and builds directly on the YT-101 executor foundation and YT-102 metadata standards rather than introducing a new integration package, storage layer, or public service surface.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `subscriptions.list` request shape and the selector modes that belong in the wrapper contract for this slice.
- Decide how to model `channelId`, `id`, `mine`, `myRecentSubscribers`, and `mySubscribers` so later layers can reuse the wrapper safely.
- Decide how to make OAuth requirements explicit for owner-scoped and subscriber-management selector modes while preserving public-compatible paths.
- Decide how to represent paging and ordering boundaries so collection-style retrieval remains reviewable without broadening the endpoint contract.
- Decide which current modules and tests provide the minimum-change implementation seam for one endpoint-specific subscriptions wrapper.
- Decide what contract artifacts later subscription-dependent features should rely on when reusing `subscriptions.list`.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the YT-141 spec against the current Layer 1 foundation to make the missing endpoint-specific behavior explicit, especially required request parts, selector exclusivity, quota visibility, paging and ordering boundaries, mixed-auth behavior, and clear distinction between invalid requests, under-authorized requests, empty-result outcomes, and successful subscription retrieval.
- **Green**: Resolve the request-shape, selector-auth, paging and ordering, implementation-seam, and contract-surface decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping decisions into one minimal strategy that extends the existing Layer 1 abstractions instead of adding a new wrapper model, transport surface, or public-facing contract prematurely.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model the `subscriptions.list` wrapper metadata, request shape, selector rules, paging and ordering behavior, OAuth guidance, and valid retrieval outcomes needed for this endpoint-specific slice.
- Define the internal contract artifacts that future subscription authors will use to understand the wrapper's quota behavior, supported selector modes, selector exclusivity, collection-versus-direct lookup behavior, and under-authorized request boundaries.
- Provide a concrete quickstart that describes how to implement the feature in Red-Green-Refactor order while preserving the current Layer 1 execution flow and reviewability expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing design expectations for `subscriptions.list` metadata completeness, quota visibility, OAuth explanation, selector visibility, paging and ordering guidance, and failure-boundary clarity before implementation tasks begin.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-filter-modes-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/quickstart.md` with only the design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contracts, and quickstart; confirm the design still preserves internal-only scope and the existing executor-based foundation; and re-check that the design remains the smallest change that satisfies the spec.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-filter-modes-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Subscription Lists Through a Stable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `subscriptions.list` is not yet available as a typed Layer 1 wrapper with explicit selector coverage, paging and ordering guidance, and normalized subscription-result handling.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `subscriptions.list` metadata, validate supported selector and optional request fields, enforce selector-auth compatibility, and execute through the existing shared executor path.
- **Refactor**: Consolidate selector naming and request-shape validation so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Understand Filter Modes, Quota, and OAuth Boundaries Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine the quota cost, selector-mode support, selector exclusivity, collection-versus-direct lookup behavior, or OAuth path clearly enough for reuse decisions.
- **Green**: Implement the smallest metadata and validation changes needed to model `subscriptions.list` as a mixed or conditional wrapper with clear maintainer-facing notes for selector support, paging and ordering boundaries, and OAuth-backed subscriber-management paths.
- **Refactor**: Remove duplicated quota, selector, and auth guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Distinguish Invalid, Unsupported, and Under-Authorized Requests Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing selectors, unsupported selector combinations, unsupported paging or ordering usage, under-authorized private selector paths, empty-result outcomes, and normalized upstream subscription-list failures clearly enough for downstream planning.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, OAuth-dependent selector behavior, empty-result success handling, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-141 stays a single-endpoint Layer 1 slice rather than growing into broader subscription tooling, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `subscriptions.list` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-141 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression protection for required `part`, selector exclusivity, selector-aware auth enforcement, paging and ordering boundaries, quota visibility, consumer-summary reviewability, empty-result handling, and the `invalid_request` versus access-related versus normalized upstream-failure boundaries so later endpoint slices cannot silently blur subscription-list behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, consumer summaries, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, API keys, OAuth tokens, or raw request credentials in any contract artifact, docstring, or test expectation.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `subscriptions.list`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
