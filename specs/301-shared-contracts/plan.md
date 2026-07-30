# Implementation Plan: YT-301 Layer 3 Shared Scaffolding and Contracts

**Branch**: `301-shared-contracts` | **Date**: 2026-07-28 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Define the shared Layer 3 public MCP tool contract and implementation scaffolding that every higher-level YouTube tool slice will depend on. The plan introduces contract artifacts for grouped public names, stable repeated parameters, response-field provenance, heuristic disclosures, ranking and filtering semantics, composition boundaries, family-oriented layout, and representative validation examples without implementing individual Layer 3 public tools in this slice.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing Layer 2 shared YouTube contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 YouTube integration resource modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; Layer 3 contract metadata, representative examples, validation fixtures, and planning artifacts remain in memory or file-based only  
**Testing**: `python3 -m pytest` for full repository validation; targeted Layer 3 unit, contract, and integration-style tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/contracts/`
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing higher-level public YouTube tools backed by lower-level YouTube contracts and integrations  
**Performance Goals**: A maintainer can derive correct grouped public names for all 19 initial Layer 3 tools in under 10 minutes; a future Layer 3 author can identify family placement in under 3 minutes; reviewers can classify at least 20 representative response fields by provenance with 100% agreement  
**Constraints**: Do not add individual Layer 3 tool behavior in this slice beyond representative non-executing examples; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; keep Layer 3 clearly distinct from near-raw Layer 2 endpoint tools; expose auth, quota, partial-result, and heuristic caveats before callers rely on results; avoid secrets, OAuth tokens, API keys, stack traces, signed URLs, raw media payloads, and sensitive owner context in public metadata, examples, errors, docs, or logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One shared Layer 3 scaffolding slice covering the 19-tool initial public catalog across `videos_*`, `channels_*`, `playlists_*`, and `transcripts_*`, at least eight representative contract examples, shared repeated-parameter conventions, response provenance categories, heuristic/ranking/filtering semantics, composition boundaries, family layout guidance, and validation evidence for later YT-302+ slices

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

- YT-301 is contract-first by design: `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/contracts/public-tool-contract.md` defines the MCP-facing Layer 3 public tool contract, while `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/contracts/shared-scaffolding-contract.md` defines the internal family layout and shared dependency contract for later tool slices.
- No concrete Layer 3 public tool behavior is planned in this slice; implementation must be limited to shared contract records, reusable conventions, representative examples, and validation expectations that later YT-302+ slices can consume.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must begin from failing or characterization checks for missing naming, repeated-parameter, response-provenance, heuristic-disclosure, ranking/filtering, composition-boundary, and family-layout compliance.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for Layer 3 contract records, naming helpers, parameter convention helpers, response provenance validators, heuristic disclosure helpers, ranking/filter declarations, composition-boundary validators, family scaffolding maps, representative examples, or discovery metadata adapters must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by safe public metadata, no secret leakage, explicit auth/quota/partial-result caveats, preservation of existing request-context and logging boundaries, reuse of Layer 1 and Layer 2 contracts, and a no-concrete-tool-implementation scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── public-tool-contract.md
│   └── shared-scaffolding-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/
└── mcp_server/
    ├── tools/
    │   ├── dispatcher.py
    │   ├── youtube_common/
    │   │   ├── contracts.py
    │   │   ├── conventions.py
    │   │   ├── examples.py
    │   │   └── families.py
    │   └── youtube_composed/
    │       ├── __init__.py
    │       ├── contracts.py
    │       ├── conventions.py
    │       ├── examples.py
    │       ├── families.py
    │       ├── videos.py
    │       ├── channels.py
    │       ├── playlists.py
    │       └── transcripts.py
    └── integrations/
        └── resources/
            ├── captions.py
            ├── channels.py
            ├── playlist_items.py
            ├── playlists.py
            ├── search.py
            └── videos.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_composed_shared_contract.py
│   └── test_youtube_composed_tool_catalog_contract.py
├── integration/
│   └── test_youtube_composed_tool_registration.py
└── unit/
    └── test_youtube_composed_shared_scaffolding.py
```

**Structure Decision**: Keep YT-301 in the existing single Python MCP service. Add a new Layer 3-oriented shared package under `src/mcp_server/tools/youtube_composed/` so higher-level composed contracts are visibly distinct from the existing near-raw Layer 2 `youtube_common` primitives, while still reusing Layer 2 and Layer 1 metadata where composition decisions need upstream identity, auth, quota, and response-boundary information. The family modules are scaffolding targets for cohesive later slices, not concrete public tool implementations in this feature.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm how Layer 3 shared scaffolding should build on YT-201/YT-202 Layer 2 contracts without duplicating near-raw endpoint rules.
- Resolve the Layer 3 package and family layout that keeps `videos_*`, `channels_*`, `playlists_*`, and `transcripts_*` cohesive.
- Confirm grouped public naming rules for all 19 initial Layer 3 tools.
- Confirm stable repeated-parameter conventions for IDs, queries, language, result limits, ordering, selected parts, date filters, pagination, and fan-out bounds.
- Confirm response provenance categories that distinguish raw upstream fields, normalized fields, and heuristic or inferred fields.
- Confirm heuristic disclosure requirements for creator classification, contact extraction, latest-upload signals, subscriber bands, ranking scores, transcript matches, and playlist fan-out.
- Confirm ranking/filtering vocabulary and composition-boundary disclosures for direct retrieval, normalization, enrichment, server-side filtering, ranking, and multi-resource fan-out.
- Confirm Python docstring and full-suite verification obligations from the constitution for any shared Layer 3 code changed by this slice.

### Research Tasks

- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md` for Layer 3 public catalog and shared contract requirements.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/` for reusable lower-layer contract primitives and boundaries.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and existing registration tests for MCP discovery, schema, and result metadata expectations that Layer 3 tools must eventually satisfy.
- Review representative Layer 1 modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/` for composition dependencies used by later Layer 3 tools without planning new upstream execution in this slice.

### Phase 0 Red-Green-Refactor

- **Red**: Capture every unresolved Layer 3 naming, repeated-parameter, response-provenance, heuristic-disclosure, ranking/filtering, composition-boundary, package-layout, docstring, and verification decision as a research topic before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/research.md` with concrete decisions and alternatives considered.
- **Refactor**: Remove duplicated Layer 2 endpoint detail from research notes and keep YT-301 focused on higher-level public tool contracts, family scaffolding, and validation expectations.

## Phase 1: Design and Contracts

### Design Goals

- Define the Layer 3 public tool contract that later tools follow for grouped names, descriptions, inputs, response field categories, heuristic disclosures, ranking/filtering behavior, composition notes, auth and quota caveats, partial results, and safe errors.
- Define internal scaffolding rules so family-specific definitions, schemas, composed handlers, reusable helpers, representative examples, tests, and caveat notes stay organized by videos, channels, playlists, and transcripts.
- Model the shared entities that later Layer 3 slices will instantiate, including tool contracts, tool families, shared parameter conventions, response field categories, heuristic disclosures, ranking/filtering rules, composition boundaries, family scaffolding contracts, and validation evidence.
- Keep this slice limited to shared contracts and representative validation examples; individual public tool behavior belongs to later YT-302+ slices.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/contracts/public-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/contracts/shared-scaffolding-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-shared-contracts/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current repo artifacts do not yet define Layer 3 public tool entities, grouped naming, repeated-parameter semantics, response-provenance rules, heuristic disclosures, composition boundaries, family placement rules, or downstream YT-302+ dependency rules clearly enough for implementation tasking.
- **Green**: Produce the data model, public tool contract, scaffolding contract, and quickstart artifacts with enough specificity to drive future tests and implementation without adding concrete Layer 3 public tools.
- **Refactor**: Deduplicate wording across design artifacts, keep the no-tool-implementation boundary explicit, and re-check that the design stays contract-first, simple, secure, observable, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Define Layer 3 Public Contracts Once

- **Red**: Add failing contract tests proving shared Layer 3 metadata is incomplete unless a representative tool declares grouped public name, family, shared parameters, response field categories, heuristic disclosures where applicable, composition boundary, lower-layer dependencies, auth/quota caveats, partial-result behavior, safe error categories, and review evidence.
- **Green**: Implement the minimum shared Layer 3 contract records, naming validation, parameter convention records, response provenance declarations, composition-boundary metadata, and representative examples needed for later tool slices to derive consistent public contracts.
- **Refactor**: Consolidate duplicate contract wording, tighten docstrings and examples, keep Layer 2 references as dependencies rather than copied rules, and run focused Layer 3 contract/unit checks before moving to family organization work.

### User Story 2 - Use Public Tools With Predictable Results

- **Red**: Add failing checks for representative Layer 3 results showing ambiguous raw, normalized, or heuristic fields; missing heuristic basis or limitation notes; unsupported repeated parameters; missing default/bound rules; missing partial-result notes; and missing auth/quota caveats for composed workflows.
- **Green**: Add the smallest shared response-provenance, heuristic-disclosure, ranking/filtering, and repeated-parameter helpers or fixtures needed for representative examples to pass while staying MCP-safe and user-facing.
- **Refactor**: Remove tool-specific special cases from shared helpers, verify examples exclude secrets and stack traces, confirm heuristic fields remain visibly inferred, and run focused response/provenance checks.

### User Story 3 - Keep Higher-Level Tool Families Cohesive

- **Red**: Add failing tests or documentation checks proving that a future Layer 3 author cannot yet identify where to place family tool definitions, input contracts, composed handlers, schemas, reusable composition helpers, examples, caveats, and tests.
- **Green**: Define the minimum family scaffolding map, export expectations, and test placement guidance needed for YT-302+ slices to add `videos_*`, `channels_*`, `playlists_*`, and `transcripts_*` tools without a monolithic shared implementation file.
- **Refactor**: Keep shared scaffolding centralized, remove duplicate family guidance, ensure all changed Python functions have reStructuredText docstrings, and rerun focused Layer 3 family-layout checks.

### Regression Strategy

- Preserve existing MCP registry, dispatcher, baseline tools, retrieval tools, hosted transport, Layer 1 endpoint wrappers, and Layer 2 endpoint-backed public tool contracts.
- Treat YT-301 as shared scaffolding only; any accidental concrete public Layer 3 tool implementation must move to the relevant YT-302+ slice.
- Use representative contract tests before any shared helper is added, then targeted unit and integration-style tests for naming, parameter conventions, response provenance, heuristic disclosure, ranking/filtering semantics, composition boundaries, safe errors, and family registration/discovery shape.
- Run targeted checks such as `python3 -m pytest tests/unit/test_youtube_composed_shared_scaffolding.py tests/contract/test_youtube_composed_shared_contract.py tests/contract/test_youtube_composed_tool_catalog_contract.py tests/integration/test_youtube_composed_tool_registration.py` before final validation.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep Layer 3 shared contracts additive until concrete YT-302+ tools depend on them, so rollback can remove the shared package and validation fixtures without changing existing public tools.
- Keep representative examples non-executing so a failed example does not affect production tool invocation.
- Avoid new dependencies, persistence, hosted routes, or broad dispatcher rewrites; use existing registry, Layer 1 resource modules, and Layer 2 contract metadata.
- Require safe public metadata and examples that exclude credentials, tokens, stack traces, signed URLs, raw media payloads, private owner context, and misleading heuristic certainty.

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

- Feature-local contracts define the MCP-facing Layer 3 public tool standard and internal family scaffolding that later YT-302+ slices must honor.
- No constitution exceptions are required because the plan uses the existing Python MCP service, existing registry, lower-layer YouTube contracts, and Layer 1 resource modules without adding infrastructure or concrete public tool behavior.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing or characterization tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including contract records, naming validators, parameter helpers, response provenance validators, heuristic disclosure helpers, ranking/filtering declarations, composition-boundary helpers, family maps, and representative example builders.
- Security, observability, and simplicity are addressed by safe caller-facing metadata, auth/quota and partial-result visibility, no secret leakage, existing request-context preservation, Layer 2/Layer 1 reuse, and a no-concrete-tool-implementation scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
