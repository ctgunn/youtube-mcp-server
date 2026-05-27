# Implementation Plan: YT-203 Layer 2 Tool `activities_list`

**Branch**: `203-activities-list` | **Date**: 2026-05-26 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the first concrete Layer 2 endpoint-backed YouTube public MCP tool, `activities_list`, mapped to the upstream `activities.list` operation. The technical approach reuses the existing YT-201/YT-202 shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/` and the existing YT-103 Layer 1 `activities.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py`, adding only the endpoint-specific public tool contract, handler, discovery metadata, validation, examples, registration, and tests required for this one low-level tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `activities.list` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, and representative results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `activities_list` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, handler adapters, response normalizers, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can determine quota and auth requirements for `activities_list` in under 1 minute; a power user can discover the selector and pagination contract and prepare a valid first request in under 3 minutes; representative valid requests preserve activity items, empty collections, requested parts, and pagination details consistently  
**Constraints**: Scope is limited to the single `activities_list` Layer 2 tool; preserve near-raw `activities.list` semantics; do not add Layer 3 enrichment, ranking, transcript lookup, channel expansion, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `1` before invocation; protect API keys, OAuth tokens, stack traces, signed URLs, raw media payloads, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`activities.list`), selector validation for `channelId`, `mine`, and deprecated `home`, required `part` selection, optional pagination and date/region filters, mixed/conditional auth disclosure, successful empty-result handling, near-raw activity collection results, and focused contract/unit/integration coverage

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

- YT-203 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/contracts/activities-list-tool-contract.md` defines the MCP-facing `activities_list` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts and the YT-103 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `activities_list` discovery, metadata, schema, selector validation, handler behavior, pagination, empty-result behavior, auth error behavior, and error mapping.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `activities_list` contracts, schema builders, validators, handler adapters, response normalizers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth disclosure, safe public metadata, no secret leakage, reuse of shared request context and error categories, and the one-endpoint scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── activities-list-tool-contract.md
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
    │       ├── activities.py
    │       ├── contracts.py
    │       ├── conventions.py
    │       ├── examples.py
    │       └── families.py
    ├── protocol/
    │   └── methods.py
    └── integrations/
        └── resources/
            ├── activities.py
            └── consumers/
                └── activities.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_activities_contract.py
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_layer1_activities_contract.py
├── integration/
│   ├── test_youtube_activities_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_activities.py
    ├── test_youtube_common_scaffolding.py
    ├── test_list_tools_method.py
    ├── test_method_routing.py
    └── test_layer1_foundation.py
```

**Structure Decision**: Keep YT-203 inside the existing single Python MCP service. Add endpoint-specific behavior through the shared YouTube Layer 2 tool surfaces and the existing activities Layer 1 wrapper rather than creating a separate service, persistence layer, or monolithic YouTube endpoint module. The concrete activities public tool should live in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` and export through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope if default public registration or discovery metadata must change; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the official `activities.list` request contract: required `part`, selector set, pagination fields, optional filters, request body rule, quota cost, response shape, and deprecated caveats.
- Confirm how `activities_list` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, and error rules.
- Confirm how the existing YT-103 Layer 1 `activities.list` wrapper exposes endpoint identity, selector validation, conditional auth, quota cost, and execution.
- Confirm the minimal public tool registration and discovery path needed for the first concrete Layer 2 endpoint tool.
- Confirm response handling for successful items, successful empty collections, pagination tokens, requested parts, and safe upstream failure categories.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `activities.list` documentation for current quota, parameters, response shape, and deprecation notes.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/activities.py` for Layer 1 execution and consumer patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `activities.list` selector, auth, quota, pagination, response, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-203 focused on the concrete `activities_list` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `activities_list` public MCP tool metadata, input schema expectations, result shape, usage notes, auth disclosure, quota disclosure, and availability caveats.
- Model the caller-facing request entities: selector mode, part selection, pagination cursor, optional filters, authorization requirement, activity collection result, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no higher-level enrichment.
- Provide a quick verification path that proves discovery, valid calls, pagination, empty results, invalid selector rejection, auth-sensitive rejection, and safe error mapping.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/contracts/activities-list-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors do not yet provide an executable public `activities_list` tool, endpoint-specific schema, handler behavior, registration path, discovery metadata retention, selector exclusivity enforcement, or activity result contract.
- **Green**: Produce the data model, `activities_list` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Channel Activity Through a Public Tool

- **Red**: Add failing contract/integration checks proving `activities_list` is absent from discovery/registration and cannot yet return a valid channel activity collection with requested parts and pagination fields preserved.
- **Green**: Add the minimum public tool definition, schema, handler adapter, registration path, and response mapping needed to call the existing Layer 1 `activities.list` capability for supported channel-based requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`.
- **Refactor**: Consolidate response-shape helpers with existing Layer 2 conventions, verify empty collections remain successful, confirm reStructuredText docstrings on changed functions, and run focused `activities_list` checks.

### User Story 2 - Understand Cost and Access Before Calling

- **Red**: Add failing discovery/contract checks proving `activities_list` metadata, description, and usage notes must expose upstream identity `activities.list`, quota cost `1`, mixed/conditional auth, active/deprecated caveats, and selector-specific access requirements. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, auth, and caveats before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `activities_list` metadata is available.
- **Refactor**: Remove duplicated quota/auth wording, keep metadata safe for public discovery, verify no secrets or stack traces appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported Activity Requests Clearly

- **Red**: Add failing unit and contract tests for missing selector, multiple selectors, unsupported optional fields or values, authorization-sensitive selector without eligible authorization, and upstream failure categories. Include explicit coverage for selector exclusivity because the current dispatcher composed-schema helper only checks that one required combination is present and does not enforce exactly-one semantics.
- **Green**: Add the minimum selector validation, auth preflight, schema rules, and safe error mapping needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `activities_list` tool unless a small shared validator is clearly reusable by later endpoint slices.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `activities.list`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, and YT-201/YT-202 representative examples.
- Treat `activities_list` as the first concrete endpoint-backed Layer 2 public tool; do not convert representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper: `python3 -m pytest tests/contract/test_layer1_activities_contract.py tests/unit/test_layer1_foundation.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `activities_list` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private channel data, signed URLs, and raw media payloads.
- Prefer contract and handler helpers local to `activities_list` over broad dispatcher or transport rewrites.

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

- Feature-local contracts define the MCP-facing `activities_list` behavior, including discovery metadata, input schema, result shape, examples, and failure categories.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, and Layer 1 `activities.list` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth visibility, MCP-safe error categories, no secret leakage, and a single-endpoint scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
