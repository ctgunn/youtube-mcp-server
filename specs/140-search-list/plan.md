# Implementation Plan: YT-140 Layer 1 Endpoint `search.list`

**Branch**: `140-search-list` | **Date**: 2026-05-02 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md)
**Input**: Feature specification from `/specs/140-search-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `search.list` by extending the existing YT-101 and YT-102 integration foundation with a concrete search contract. The plan keeps the feature internal-only, models `search.list` as a high-quota `GET /search` wrapper with required `part` and `q`, preserves near-raw optional search refinements for search type, pagination, date filtering, language and region scoping, and restricted filter modes, and makes the wrapper reviewable as a mixed or conditional-auth operation with a documented quota caveat, deterministic invalid-combination handling, and normalized populated versus empty versus failed search outcomes.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, and search execution state remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `search.list` quota cost, quota caveat, conditional authorization behavior, supported search refinements, and empty-result handling reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, keep the high-cost `100`-unit search quota highly visible, reject unsupported or incompatible search refinements deterministically before execution where the wrapper defines them, keep secrets and tokens out of docs and logs, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `search.list` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later search-dependent work

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

- YT-140 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later search-driven work.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, required search inputs, quota cost, quota caveat, conditional auth expectations, supported search refinements, and failure behavior.

## Project Structure

### Documentation (this feature)

```text
specs/140-search-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-search-list-wrapper-contract.md
│   └── layer1-search-list-auth-refinement-contract.md
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
│   └── test_layer1_metadata_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Extend the existing single-package Python service under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/` and preserve the repository's `tests/unit`, `tests/contract`, and `tests/integration` layering. YT-140 stays internal-only and builds directly on the YT-101 executor foundation and YT-102 metadata standards rather than introducing a new integration package, storage layer, or public service surface.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide the minimum supported `search.list` request shape and the optional search refinements that belong in the wrapper contract for this slice.
- Decide how to model search-type handling, pagination, date filtering, and language or region refinements so later layers can reuse the wrapper safely.
- Decide how to resolve the repository-local tension between API-key search expectations and the existing conditional-auth metadata examples for `search`.
- Decide how to make the `100`-unit quota cost and the known quota-documentation caveat visible enough for downstream reuse decisions.
- Decide which current modules and tests provide the minimum-change implementation seam for one endpoint-specific search wrapper.
- Decide what contract artifacts later search-dependent features should rely on when reusing `search.list`.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the YT-140 spec against the current Layer 1 foundation to make the missing endpoint-specific behavior explicit, especially required search inputs, high-quota visibility, quota caveat handling, conditional authorization, supported refinement categories, and clear distinction between invalid requests, restricted-request failures, empty-result outcomes, and successful search results.
- **Green**: Resolve the request-shape, auth-mode, refinement-boundary, quota-caveat, implementation-seam, and contract-surface decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping decisions into one minimal strategy that extends the existing Layer 1 abstractions instead of adding a second wrapper model, new transport surface, or public-facing contract prematurely.

### Research Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/research.md`

## Phase 1: Design and Contracts

### Design Focus

- Model the `search.list` wrapper metadata, request shape, refinement rules, conditional-auth guidance, and valid search outcomes needed for this endpoint-specific slice.
- Define the internal contract artifacts that future search authors will use to understand the wrapper's quota behavior, quota caveat, supported search-type behavior, pagination, date filtering, language and region scoping, and restricted-filter boundaries.
- Provide a concrete quickstart that describes how to implement the feature in Red-Green-Refactor order while preserving the current Layer 1 execution flow and reviewability expectations.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing design expectations for `search.list` metadata completeness, quota and caveat visibility, conditional-auth explanation, supported refinement visibility, and failure-boundary clarity before implementation tasks begin.
- **Green**: Produce `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-auth-refinement-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/quickstart.md` with only the design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contracts, and quickstart; confirm the design still preserves internal-only scope and the existing executor-based foundation; and re-check that the design remains the smallest change that satisfies the spec.

### Design Outputs

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-auth-refinement-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Run a Reusable Search Query Through Layer 1

- **Red**: Add failing unit and integration tests proving `search.list` is not yet available as a typed Layer 1 wrapper with explicit request-shape, metadata, and normalized search-result coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `search.list` metadata, validate supported required inputs and refinements, and execute through the existing shared executor path.
- **Refactor**: Consolidate wrapper naming and request-shape validation so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Understand Search Scope, Quota, and Refinement Options Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine the quota cost, quota caveat, conditional-auth path, supported search-type behavior, pagination semantics, or language and region refinements clearly enough for reuse decisions.
- **Green**: Implement the smallest metadata and validation changes needed to model `search.list` as a mixed or conditional wrapper with clear maintainer-facing notes for supported refinements, restricted-filter paths, quota cost, and quota caveat visibility.
- **Refactor**: Remove duplicated quota and refinement guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Distinguish Invalid, Unsupported, and Restricted Search Requests Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing search inputs, unsupported refinement combinations, restricted-filter authorization failures, empty-result searches, and normalized upstream search failures clearly enough for downstream search planning.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, conditional authorization, empty-result success handling, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-140 stays a single-endpoint Layer 1 slice rather than growing into broader search tooling, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `search.list` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-140 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression protection for required search inputs, refinement validation, high-quota visibility, quota caveat visibility, consumer-summary reviewability, empty-result handling, and the `invalid_request` versus restricted-auth versus normalized upstream-failure boundaries so later endpoint slices cannot silently blur search behavior.

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

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `search.list`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
