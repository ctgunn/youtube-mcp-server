# Implementation Plan: YT-142 Layer 1 Endpoint `subscriptions.insert`

**Branch**: `142-subscriptions-insert` | **Date**: 2026-05-04 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md)
**Input**: Feature specification from `/specs/142-subscriptions-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `subscriptions.insert` by extending the existing YT-101 and YT-102 integration foundation with a concrete OAuth-required write contract. The plan models one deterministic subscription-creation path centered on `part=snippet` plus a writable target-subscription body, keeps the official 50-unit quota and OAuth requirement reviewable in metadata and contracts, preserves normalized success versus validation versus access versus upstream-create failure boundaries, and avoids introducing any new public MCP tool surface.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and subscription-create execution state remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `subscriptions.insert` quota, OAuth-only write expectations, supported writable-part usage, and normalized create outcomes reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, keep the official quota cost `50` visible in review surfaces, require deterministic rejection of unsupported or malformed create inputs before execution where the wrapper defines them, keep secrets and tokens out of docs and logs, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `subscriptions.insert` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later subscription-management work

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

- YT-142 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later subscription-management work.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, writable-part rules, OAuth expectations, target-subscription validation, quota cost, and normalized failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/142-subscriptions-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-subscriptions-insert-wrapper-contract.md
│   └── layer1-subscriptions-insert-auth-write-contract.md
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
│   └── test_layer1_subscriptions_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the repository's `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-142 stays internal-only and builds directly on the YT-101 executor foundation and YT-102 metadata standards rather than introducing a new integration package, storage layer, or public service surface.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `subscriptions.insert` request shape and the writable target-subscription fields that belong in the wrapper contract for this slice.
- Decide how to model `part=snippet`, the writable body payload, and the minimum target channel relationship so later layers can reuse the wrapper safely.
- Decide how to make OAuth-required access explicit while keeping create-boundary and duplicate or ineligible-target behavior reviewable.
- Decide which current modules and tests provide the minimum-change implementation seam for one endpoint-specific subscriptions write wrapper.
- Decide what contract artifacts later subscription-management features should rely on when reusing `subscriptions.insert`.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the YT-142 spec against the current Layer 1 foundation to make the missing endpoint-specific behavior explicit, especially required request parts, writable target-subscription shape, quota visibility, OAuth-only behavior, and clear distinction between invalid requests, access failures, duplicate or ineligible target failures, and successful subscription creation.
- **Green**: Resolve the request-shape, writable-boundary, auth, implementation-seam, and contract-surface decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping decisions into one minimal strategy that extends the existing Layer 1 abstractions instead of adding a new wrapper model, transport surface, or public-facing contract prematurely.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model the `subscriptions.insert` wrapper metadata, request shape, writable target-subscription rules, OAuth guidance, and valid create outcomes needed for this endpoint-specific slice.
- Define the internal contract artifacts that future subscription authors will use to understand the wrapper's quota behavior, supported writable-part usage, target-channel boundary, and under-authorized or duplicate-request boundaries.
- Provide a concrete quickstart that describes how to implement the feature in Red-Green-Refactor order while preserving the current Layer 1 execution flow and reviewability expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing design expectations for `subscriptions.insert` metadata completeness, quota visibility, OAuth explanation, writable-part support, target-channel validation, and failure-boundary clarity before implementation tasks begin.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-auth-write-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md` with only the design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contracts, and quickstart; confirm the design still preserves internal-only scope and the existing executor-based foundation; and re-check that the design remains the smallest change that satisfies the spec.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-auth-write-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Create a Subscription Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `subscriptions.insert` is not yet available as a typed Layer 1 wrapper with explicit writable target-subscription coverage and normalized subscription-create result handling.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `subscriptions.insert` metadata, validate supported writable request fields, enforce OAuth-required access, and execute through the existing shared executor path.
- **Refactor**: Consolidate writable-field naming and request-shape validation so the new endpoint-specific behavior fits the current Layer 1 mutation pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Review Quota, OAuth, and Writable-Part Expectations Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine the quota cost, OAuth-only access rule, supported writable part, or minimum target-subscription inputs clearly enough for reuse decisions.
- **Green**: Implement the smallest metadata and validation changes needed to model `subscriptions.insert` as an OAuth-required wrapper with clear maintainer-facing notes for writable-part support, target-channel requirements, and unsupported optional write fields or mutation shapes.
- **Refactor**: Remove duplicated quota, auth, and write-boundary guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Reject Invalid, Duplicate, or Unauthorized Subscription Requests Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing target-subscription details, unsupported writable parts, duplicate or ineligible target relationships, under-authorized requests, and normalized upstream create failures clearly enough for downstream planning.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, OAuth-only create behavior, duplicate or ineligible target outcomes, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-142 stays a single-endpoint Layer 1 slice rather than growing into broader subscription-management tooling, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `subscriptions.insert` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-142 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression protection for required `part`, writable target-subscription validation, OAuth-only enforcement, quota visibility, consumer-summary reviewability, and the `invalid_request` versus access-related versus normalized upstream-create-failure boundaries so later endpoint slices cannot silently blur subscription-creation behavior.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `subscriptions.insert`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
