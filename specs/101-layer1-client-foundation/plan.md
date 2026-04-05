# Implementation Plan: YT-101 Layer 1 Shared Client Foundation

**Branch**: `101-layer1-client-foundation` | **Date**: 2026-04-04 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/spec.md)
**Input**: Feature specification from `/specs/101-layer1-client-foundation/spec.md`

## Summary

Build the internal Layer 1 foundation that future YouTube endpoint wrappers and higher-layer workflows will share. The plan centers on a dedicated integration module under `src/mcp_server/`, a metadata-first wrapper contract, shared request execution and auth policy handling, normalized upstream failures, executor-level observability hooks, and representative test coverage proving one wrapper and one higher-layer consumer can reuse the same foundation.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis-compatible session support, Python standard-library JSON/HTTP/config/logging tooling  
**Storage**: In-memory runtime state only for request handling and integration metadata; no new persistent storage introduced by this feature  
**Testing**: `pytest` for unit, integration, and contract coverage; `ruff check .` for linting  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature artifacts under `specs/101-layer1-client-foundation/`  
**Target Platform**: Linux-hosted Python service for local and Cloud Run execution paths  
**Project Type**: Python MCP web service  
**Performance Goals**: A maintainer can add a representative Layer 1 wrapper using the shared foundation in under 15 minutes, and representative higher-layer consumers can reuse typed integration methods without adding one-off request logic  
**Constraints**: Keep Layer 1 internal-only, preserve MCP/public tool behavior, require explicit Red-Green-Refactor sequencing, require full-suite validation before completion, avoid secret exposure in logs, and add reStructuredText docstrings to all new or changed Python functions  
**Scale/Scope**: One shared Layer 1 foundation, one representative wrapper, one representative higher-layer consumer path, and supporting contract/test/documentation artifacts that unblock the broader YT-1xx series

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

**Initial Gate Result**: PASS

**Constitution Notes**:

- YT-101 does not add a new public MCP tool, but it does establish an internal contract consumed by future public layers. That contract is documented in [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md).
- Red-Green-Refactor work is planned separately for the representative wrapper contract, shared executor behavior, and higher-layer consumer seam.
- Full-suite validation command for feature completion is `python3 -m pytest` from the repository root plus `ruff check .`.
- Observability remains executor-bound to keep logs consistent and to avoid per-wrapper ad hoc logging.
- Security remains centered on auth policy handling and log redaction; no secrets are to be embedded in code, tests, or logs.
- No constitution exceptions are required for this feature.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── layer1-wrapper-contract.md
│   └── layer1-consumer-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/
└── mcp_server/
    ├── app.py
    ├── config.py
    ├── observability.py
    ├── protocol/
    ├── tools/
    └── transport/

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Use the existing single Python service structure under `src/mcp_server/` and `tests/`. YT-101 should introduce an internal integration-oriented module under `src/mcp_server/` rather than placing upstream client behavior in `tools/`, because this preserves the project’s transport/protocol/tool separation and scales better for the YT-1xx endpoint inventory.

## Phase 0: Research

### Research Focus

- Best-practice structure for an internal Layer 1 integration foundation in this repository
- Metadata-first wrapper contracts that capture endpoint identity, auth mode, quota, and lifecycle notes
- Retry, logging, and normalized upstream error patterns suitable for future higher-layer reuse
- Test strategy that matches the repository’s `unit` / `integration` / `contract` split

### Research Output

- Consolidate decisions in [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/research.md)
- Resolve all planning unknowns before implementation task generation

### Red-Green-Refactor Plan

- **Red**: Identify failing tests needed to prove wrapper metadata requirements, auth policy handling, retry classification, observability hooks, and higher-layer typed consumption.
- **Green**: Choose the smallest internal contract and module layout that can satisfy one representative wrapper and one representative consumer without widening scope to the full endpoint inventory.
- **Refactor**: Simplify the contract surface, remove speculative abstractions, and keep the design narrow enough for YT-102 and later endpoint slices to extend cleanly.

## Phase 1: Design and Contracts

### Planned Design Artifacts

- Data model: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/data-model.md)
- Contract document: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md)
- Consumer contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-consumer-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-consumer-contract.md)
- Quickstart: [/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/quickstart.md)

### Likely Code Touch Points

- `src/mcp_server/` for the new internal Layer 1 integration module and shared executor/policy types
- `src/mcp_server/observability.py` for any reusable hook alignment with existing structured logging patterns
- `tests/unit/` for metadata, auth policy, and normalized error behavior
- `tests/integration/` for executor-plus-wrapper behavior
- `tests/contract/` for higher-layer typed-consumer expectations and internal contract regression coverage

### Red-Green-Refactor Plan by User Story

**User Story 1: Add Endpoint Wrappers Consistently**

- **Red**: Add failing unit tests showing a wrapper cannot be defined without required metadata, and failing integration tests showing execution paths lack shared request, auth, retry, logging, or error behavior.
- **Green**: Implement the smallest shared metadata contract, request executor, auth policy model, and failure-normalization surface needed for one representative wrapper to pass.
- **Refactor**: Reduce duplication between metadata validation and execution code, clarify names, and add reStructuredText docstrings that explain purpose, inputs, outputs, and quota/auth assumptions.

**User Story 2: Consume Typed Integration Methods in Higher Layers**

- **Red**: Add failing contract or integration tests proving a representative higher-layer consumer still relies on raw request logic or cannot consume the typed Layer 1 method.
- **Green**: Implement the minimum typed wrapper interface and representative consumer seam needed to remove raw request-building from the higher layer.
- **Refactor**: Tighten typed boundaries, remove unnecessary coupling, and keep higher-layer behavior independent from upstream transport details.

**User Story 3: Review Foundation Readiness Before Expanding Coverage**

- **Red**: Add failing review-oriented checks or documentation assertions showing the shared contract is incomplete or key metadata and lifecycle notes are missing.
- **Green**: Fill the maintainer-facing contract and data model artifacts with enough detail to review the foundation in one pass.
- **Refactor**: Prune speculative fields, align wording between code and docs, and ensure follow-on YT-102 work can extend the same contract rather than replace it.

### Test and Validation Strategy

- Unit coverage for metadata validation, auth mode selection, retry classification, lifecycle-note enforcement, and normalized error mapping
- Integration coverage for representative wrapper execution through the shared executor and observability hook boundary
- Contract coverage for the internal wrapper contract and representative higher-layer consumer expectations
- Full repository validation before completion: `python3 -m pytest`
- Lint validation before completion: `ruff check .`
- All new or changed Python functions must include reStructuredText docstrings before review

## Phase 1 Deliverables

- `research.md` resolves design choices with no remaining `NEEDS CLARIFICATION` markers
- `data-model.md` defines wrapper metadata, executor policy, normalized failure, and higher-layer consumer entities
- `contracts/layer1-wrapper-contract.md` defines the internal Layer 1 wrapper contract for maintainers and downstream internal consumers
- `contracts/layer1-consumer-contract.md` defines what representative higher-layer consumers may rely on when composing typed Layer 1 methods
- `quickstart.md` shows how to extend the foundation with one new wrapper and how to verify the targeted and full-suite tests
- Agent context updated through `.specify/scripts/bash/update-agent-context.sh codex`

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

**Post-Design Gate Result**: PASS

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
