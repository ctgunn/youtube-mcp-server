# Implementation Plan: YT-202 Layer 2 Tool Metadata, Naming, and Quota Standards

**Branch**: `202-layer2-metadata-standards` | **Date**: 2026-05-24 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Tighten the Layer 2 endpoint-backed public MCP tool standard so every tool definition exposes complete upstream identity, deterministic naming, official quota cost, auth mode, availability state, quota-visible descriptions and usage notes, and a clear near-raw response boundary. The technical approach builds additively on the existing YT-201 shared Layer 2 scaffolding under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`, extending contracts, representative examples, and validation checks without implementing individual endpoint-backed tools in this slice.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing YT-201 shared Layer 2 modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 YouTube resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; metadata standards, representative examples, validation fixtures, and contract artifacts remain in memory or file-based only  
**Testing**: `python3 -m pytest` for full repository validation; targeted Layer 2 unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public tools backed by an internal YouTube integration layer  
**Performance Goals**: A maintainer can derive correct public names for at least 10 representative Layer 2 resource-method pairs in under 5 minutes; a future Layer 3 author can estimate quota and auth requirements for a three-tool Layer 2 composition in under 3 minutes  
**Constraints**: Do not add individual endpoint-backed public tool behavior in this slice beyond representative contract examples; do not introduce new persistence, external dependencies, or hosted transport changes; preserve Layer 2 as near-raw endpoint access rather than Layer 3-style composition; expose quota/auth/availability before invocation; avoid secrets, OAuth tokens, API keys, stack traces, signed URLs, and unsafe raw media payloads in public metadata, examples, errors, docs, or logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One standards slice covering future endpoint-backed tools from YT-203 through YT-255, at least 10 representative resource-method examples, metadata completeness validation, quota and usage-note visibility, deterministic naming, auth and availability declarations, and response-shaping boundary checks

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

- YT-202 is contract-first by design: `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/contracts/layer2-metadata-standards-contract.md` defines the MCP-facing Layer 2 metadata, naming, quota, auth, availability, usage-note, and response-boundary contract.
- No individual endpoint tool behavior is planned in this slice; implementation must be limited to shared metadata standards, representative examples, and validation expectations that later endpoint slices can reuse.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must begin from failing or characterization checks for missing metadata, naming, quota visibility, auth/availability declarations, usage notes, and response-boundary compliance.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for metadata records, naming validators, quota disclosure helpers, auth/availability declarations, response-boundary validators, representative example builders, or discovery metadata adapters must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth visibility, safe public metadata, no secret leakage, no hosted transport changes, and reuse of existing YT-201 scaffolding and Layer 1 boundaries.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── layer2-metadata-standards-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/
└── mcp_server/
    ├── tools/
    │   ├── dispatcher.py
    │   └── youtube_common/
    │       ├── __init__.py
    │       ├── contracts.py
    │       ├── conventions.py
    │       ├── examples.py
    │       └── families.py
    └── integrations/
        └── resources/
            ├── base.py
            ├── activities.py
            ├── captions.py
            ├── comments.py
            ├── playlist_items.py
            ├── search.py
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

**Structure Decision**: Keep YT-202 in the existing single Python MCP service. Extend the shared Layer 2 standard under `src/mcp_server/tools/youtube_common/` rather than creating a new package, persistence layer, hosted endpoint, or endpoint-family implementation. Later YT-203 through YT-255 slices should consume these standards when adding concrete public endpoint-backed tools.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm how YT-202 should build on YT-201 shared scaffolding without duplicating broad input, layout, and error conventions.
- Resolve the exact required metadata fields and visibility targets for Layer 2 tool definitions.
- Confirm deterministic naming for regular resource-method pairs and official camelCase method suffixes.
- Confirm auth-mode and availability-state vocabulary for pre-invocation caller visibility.
- Confirm how official quota costs appear in metadata, descriptions, and usage notes.
- Confirm when Layer 2 response reshaping is allowed and when a result crosses into Layer 3 composition.
- Confirm representative endpoint examples needed to prove the standard across read, paginated, mutation, media, high-quota, mixed-auth, OAuth-only, camelCase, and constrained endpoint shapes.
- Confirm Python docstring and full-suite verification obligations from the constitution for any shared code changed by this slice.

### Research Tasks

- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md` for Layer 2 metadata, naming, quota, auth, and response-boundary requirements.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` for existing YT-201 primitives that YT-202 can extend.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_shared_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer2_shared_scaffolding.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer2_tool_registration.py` for current coverage and gaps.
- Review representative Layer 1 metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/` for official quota, auth, and operation identity patterns to reference without duplicating Layer 1 execution.

### Phase 0 Red-Green-Refactor

- **Red**: Capture each unresolved metadata, naming, quota visibility, auth/availability vocabulary, response-boundary, representative example, docstring, and verification decision as a research topic before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201 scaffolding detail from research notes and keep YT-202 focused on metadata, naming, quota, auth, availability, usage-note, and response-boundary standards.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact Layer 2 metadata record that must be visible before invocation.
- Define deterministic naming rules and required examples for standard and camelCase resource-method pairs.
- Define quota disclosure rules for metadata, tool descriptions, and usage notes, including high-cost warnings.
- Define auth-mode and availability-state declarations that are machine-checkable and caller-readable.
- Define the response-shaping boundary between near-raw endpoint data, light MCP clarity wrappers, and out-of-scope Layer 3 composition.
- Model representative examples and validation evidence so future endpoint slices can be rejected when required metadata or visibility is missing.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/contracts/layer2-metadata-standards-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201 artifacts do not yet explicitly require availability state, usage-note quota visibility, high-quota warnings, metadata completeness across 10 examples, or response-boundary classification.
- **Green**: Produce the data model, metadata standards contract, and quickstart artifacts with enough specificity to drive future tests and implementation without adding concrete endpoint-backed tools.
- **Refactor**: Deduplicate wording against YT-201, keep the no-endpoint-implementation boundary explicit, and re-check that the design stays contract-first, simple, secure, observable, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Inspect Tool Identity and Cost

- **Red**: Add failing contract tests proving a Layer 2 tool definition is incomplete unless it exposes public name, upstream resource, upstream method, operation identity, official quota-unit cost, auth mode, availability state, description-level quota visibility, usage-note quota visibility, and applicable caveats.
- **Green**: Extend the minimum shared metadata record and representative examples needed for discovery and review surfaces to expose all required fields consistently.
- **Refactor**: Consolidate duplicated quota/auth/availability wording, verify safe metadata excludes secrets and stack traces, confirm reStructuredText docstrings on changed functions, and run focused metadata contract checks.

### User Story 2 - Derive Names Consistently

- **Red**: Add failing naming tests for at least 10 representative resource-method pairs, including `videos.list`, `playlists.insert`, `comments.setModerationStatus`, `videos.getRating`, media/mutation endpoints, and resource names with existing upstream casing.
- **Green**: Add or tighten the shared naming helper and representative examples so names follow `resource_method`, omit `youtube_`, preserve official camelCase method suffixes, and remain deterministic.
- **Refactor**: Remove endpoint-specific naming special cases from shared helpers, keep naming examples in one reviewable location, and run focused unit and contract checks.

### User Story 3 - Preserve Raw Endpoint Semantics With Clear Boundaries

- **Red**: Add failing checks that classify representative responses as near-raw, lightly reshaped for MCP clarity, or out of Layer 2 scope, rejecting examples that imply higher-level composition, enrichment, ranking, or heuristics.
- **Green**: Add the minimum response-boundary metadata and examples needed to describe allowed wrapper fields, raw upstream preservation, mutation acknowledgments, upload/download handling, pagination, requested parts, and non-list results.
- **Refactor**: Keep response-boundary language aligned with YT-201 response conventions, remove duplicated prose, verify no raw media or sensitive data appears in examples, and run focused response-boundary checks.

### Regression Strategy

- Preserve existing MCP registry, dispatcher, baseline tools, retrieval tools, hosted transport, and Layer 1 endpoint behavior.
- Treat YT-202 as standards and validation only; any actual endpoint-backed public tool behavior must move to the relevant YT-203 through YT-255 slice.
- Use representative contract tests before any metadata helper changes, then targeted unit and integration tests for naming, metadata validation, quota visibility, auth/availability declarations, usage notes, response boundaries, and registration/discovery metadata shape.
- Run targeted checks such as `python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py tests/integration/test_layer2_tool_registration.py` before final validation.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep metadata standard changes additive until endpoint slices depend on them, so rollback can remove or relax YT-202-specific validation without changing existing public endpoint behavior.
- Keep representative examples non-executing so a failed example does not affect production tool invocation.
- Avoid new dependencies, persistence, hosted routes, or broad dispatcher rewrites; use existing YT-201 scaffolding and Layer 1 metadata.
- Require safe public metadata and examples that exclude credentials, tokens, stack traces, signed URLs, raw media payloads, and sensitive owner/delegation details.

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

- Feature-local contracts define the MCP-facing Layer 2 metadata standards that later endpoint slices must honor.
- No constitution exceptions are required because the plan uses the existing Python MCP service, YT-201 shared Layer 2 modules, and Layer 1 resource metadata without adding infrastructure or endpoint execution.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing or characterization tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including metadata validators, naming helpers, quota disclosure helpers, auth/availability declarations, example builders, and response-boundary helpers.
- Security, observability, and simplicity are addressed by safe caller-facing metadata, quota/auth visibility, no secret leakage, reuse of existing request-context boundaries, and a no-endpoint-implementation scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
