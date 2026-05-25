# Implementation Plan: YT-201 Layer 2 Shared Scaffolding and Contracts

**Branch**: `201-layer2-shared-contracts` | **Date**: 2026-05-24 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Define the shared Layer 2 public MCP tool contract and implementation scaffolding that every endpoint-backed YouTube Data API tool slice will depend on. The plan introduces contract artifacts for tool naming, upstream identity, auth and quota visibility, input mapping, near-raw result conventions, safe error categories, resource-family layout, and representative validation examples without adding individual endpoint tool behavior in this slice.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing Python MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing Layer 1 YouTube integration resource modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`; Python standard library dataclasses, enums, JSON-compatible dictionaries, and package imports; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; Layer 2 contract metadata, representative examples, registration metadata, test fixtures, and planning artifacts remain in memory or file-based only  
**Testing**: `python3 -m pytest` for full repository validation; targeted Layer 2 unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed function, plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public tools backed by an internal YouTube integration layer  
**Performance Goals**: A maintainer can derive correct public names for 10 representative Layer 2 resource-method pairs in under 5 minutes, and a future endpoint author can identify placement and contract obligations in under 3 minutes  
**Constraints**: Do not add individual YouTube endpoint tool behavior in this slice beyond representative contract examples; do not introduce new persistence or external dependencies; keep Layer 2 near-raw rather than heuristic or composed; do not expose secrets, OAuth tokens, API keys, raw media payloads, or stack traces in tool results, errors, docs, or logs; preserve existing MCP discovery and invocation compatibility; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One shared Layer 2 contract and scaffolding slice covering future endpoint-backed tools from YT-203 through YT-255, representative read, paginated, camelCase, OAuth-only, mutation, upload/media, high-quota, and constrained/deprecated endpoint shapes, and documentation/test hooks for downstream endpoint slices

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

- YT-201 is contract-first by design: `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/layer2-public-tool-contract.md` defines the MCP-facing Layer 2 tool contract, while `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/layer2-scaffolding-contract.md` defines the internal layout and dependency contract for endpoint slices.
- No individual endpoint tool behavior is planned in this slice; the Green phase is limited to shared metadata/scaffolding surfaces and representative examples that allow later endpoint slices to depend on YT-201.
- Red-Green-Refactor is required for research, design artifacts, and each planned implementation story. Implementation must begin with failing or characterization tests for missing Layer 2 rules, representative metadata completeness, registration/discovery shape, and resource-family placement.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for naming helpers, metadata records, schema builders, registration helpers, result wrappers, error mapping helpers, or resource-family exports must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security and observability are addressed by requiring safe MCP errors, no secret leakage, quota/auth visibility, and preservation of existing request context/logging boundaries when endpoint slices later call Layer 1 wrappers.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer2-public-tool-contract.md
│   └── layer2-scaffolding-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/
└── mcp_server/
    ├── tools/
    │   ├── __init__.py
    │   ├── dispatcher.py
    │   └── retrieval.py
    └── integrations/
        └── resources/
            ├── __init__.py
            ├── activities.py
            ├── captions.py
            ├── channel_banners.py
            ├── channels.py
            ├── comments.py
            ├── comment_threads.py
            ├── playlist_items.py
            ├── playlists.py
            ├── search.py
            ├── subscriptions.py
            ├── videos.py
            └── watermarks.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_layer2_shared_contract.py
│   └── test_layer2_tool_catalog_contract.py
├── integration/
│   └── test_layer2_tool_registration.py
└── unit/
    └── test_layer2_shared_scaffolding.py
```

**Structure Decision**: Keep the feature in the existing single Python MCP service. Add shared Layer 2 surfaces under the current tool and integration organization rather than creating a new service, persistence layer, or endpoint-specific package tree. Later endpoint slices should place endpoint-specific public tools by resource family while depending on the shared Layer 2 contracts created by this slice.

## Phase 0: Research and Open Questions

### Research Focus

- Resolve where Layer 2 public tool contracts should sit relative to the existing MCP tool registry and Layer 1 resource-family integration modules.
- Confirm the public naming standard for resource-method pairs, including camelCase method suffixes and no `youtube_` prefix.
- Confirm how near-raw input and output conventions should remain close to YouTube Data API semantics while still being usable through MCP schemas, discovery, and result content.
- Confirm shared auth, quota, deprecation, availability, and error categories so endpoint slices do not redefine them.
- Confirm the minimum representative endpoint examples required to validate read, paginated, camelCase, OAuth-only, mutation, upload/media, high-quota, and constrained/deprecated shapes.
- Confirm Python docstring and full-suite verification expectations from the constitution for any shared code introduced by this slice.

### Research Tasks

- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md` for Layer 2 rules and representative endpoint shapes.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and existing MCP tool contracts for discovery, schema, registration, and result expectations.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/` and YT-156 artifacts for resource-family organization and Layer 1 dependency boundaries.
- Review existing Layer 1 contract tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_*_contract.py` for metadata, auth, quota, and response-normalization patterns that Layer 2 should reference rather than duplicate.

### Phase 0 Red-Green-Refactor

- **Red**: Capture every unresolved Layer 2 naming, placement, auth/quota/error, response convention, representative example, and docstring/testing expectation as a research topic before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/research.md` with concrete decisions and alternatives considered.
- **Refactor**: Remove duplicated or endpoint-specific implementation detail from research notes so they remain reusable by all YT-203 through YT-255 endpoint slices.

## Phase 1: Design and Contracts

### Design Goals

- Define a public Layer 2 tool contract that every endpoint-backed MCP tool can follow for names, descriptions, schemas, results, auth mode, quota visibility, caveats, and safe errors.
- Define internal scaffolding rules so endpoint-specific definitions, handlers, request contracts, representative examples, and tests stay organized by resource family while shared rules remain centralized.
- Model the shared entities that later endpoint slices will instantiate, including tool contracts, resource-method names, parameter mappings, response conventions, error categories, auth and quota declarations, resource-family placement, and verification evidence.
- Keep this slice limited to shared contracts and representative validation examples; individual endpoint behavior belongs to later YT-203 through YT-255 slices.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/layer2-public-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/layer2-scaffolding-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current repo artifacts do not yet define Layer 2 entities, public MCP tool contract expectations, resource-family placement rules, or downstream endpoint-slice dependency rules clearly enough for implementation tasking.
- **Green**: Produce the data model, public tool contract, scaffolding contract, and quickstart artifacts with enough specificity to drive future tests and implementation without adding endpoint tool behavior.
- **Refactor**: Deduplicate wording across design artifacts, keep the no-endpoint-implementation boundary explicit, and re-check that the design stays contract-first, simple, secure, observable, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Define Shared Layer 2 Contracts Once

- **Red**: Add failing contract tests proving shared Layer 2 metadata is incomplete unless a representative endpoint declares public tool name, upstream resource/method, official quota cost, auth mode, caveats when applicable, input mapping, near-raw result convention, and safe error categories.
- **Green**: Implement the minimum shared contract records, naming helper, metadata validation, and representative examples needed for later endpoint slices to derive consistent public tool contracts.
- **Refactor**: Consolidate duplicated example metadata, tighten names and docstrings, and run focused Layer 2 contract/unit checks before moving to registration-oriented work.

### User Story 2 - Use Low-Level Tools With Predictable Semantics

- **Red**: Add failing or characterization tests for representative read, paginated, camelCase, OAuth-only, mutation, upload/media, high-quota, and constrained/deprecated examples showing expected schema/result/error conventions.
- **Green**: Add the smallest shared schema/result/error convention helpers or fixtures needed for representative examples to pass while staying near-raw and MCP-safe.
- **Refactor**: Remove endpoint-specific special cases from shared helpers, ensure errors never expose secrets or stack traces, and verify examples remain close to upstream semantics without becoming Layer 3-style composed tools.

### User Story 3 - Keep Endpoint Tool Families Cohesive

- **Red**: Add failing tests or documentation checks proving that a future endpoint author cannot yet identify family-level placement for tool definitions, input contracts, handlers, response expectations, tests, caveats, and examples.
- **Green**: Define the minimum resource-family scaffolding map, export expectations, and test placement guidance needed for endpoint slices to add tools without a monolithic Layer 2 file.
- **Refactor**: Keep shared scaffolding centralized, remove duplicate family guidance, ensure all changed Python functions have reStructuredText docstrings, and rerun focused Layer 2 checks.

### Regression Strategy

- Preserve existing MCP registry, dispatcher, baseline tools, retrieval tools, hosted transport, and Layer 1 endpoint behavior.
- Treat YT-201 as shared scaffolding only; any accidental public endpoint implementation must be moved to the relevant YT-203 through YT-255 slice.
- Use representative contract tests before any implementation helper is added, then targeted unit and integration tests for naming, metadata validation, schema/result conventions, safe errors, and registration/discovery shape.
- Run targeted checks such as `python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/integration/test_layer2_tool_registration.py` before final validation.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep shared Layer 2 contracts additive until endpoint slices begin depending on them, so rollback can remove the shared metadata/scaffolding without changing existing public tools.
- Keep representative examples separate from endpoint behavior so a failed example does not affect production tool invocation.
- Avoid new dependencies, persistence, hosted route changes, or broad dispatcher rewrites; use existing registry and Layer 1 boundaries.
- Require safe error categories and no secret-bearing detail in docs, logs, test fixtures, or result examples.

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

- Feature-local contracts define the MCP-facing Layer 2 public tool standard and the internal scaffolding contract that later endpoint slices must honor.
- No constitution exceptions are required because the plan uses the existing Python MCP service, existing tool registry, and existing Layer 1 resource-family boundaries without adding new infrastructure.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing or characterization tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including naming helpers, contract validators, schema builders, result wrapper helpers, error category helpers, and registration helpers.
- Security, observability, and simplicity are addressed by safe errors, auth/quota visibility, no secret leakage, existing request-context preservation, and a no-endpoint-implementation scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
