# Implementation Plan: YT-212 Layer 2 Tool `channelSections_list`

**Branch**: `212-channel-sections-list` | **Date**: 2026-06-09 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the Layer 2 endpoint-backed YouTube public MCP tool, `channelSections_list`, mapped to upstream `channelSections.list`. The technical approach adds a focused channel-sections Layer 2 resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, reuses the YT-112 Layer 1 `channelSections.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, and adds only the endpoint-specific public tool contract, handler, selector validation, discovery metadata, examples, registration, list-result mapping, caveat disclosure, and tests required for this one low-level channel-section retrieval tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `channelSections.list` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`; existing Layer 1 channel-sections consumers, validators, and response normalizers under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channel_sections.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, selector context, caveat context, and representative channel-section collection results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `channelSections_list` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, selector helpers, auth-context helpers, result mappers, handler adapters, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can identify supported `channelSections_list` lookup modes, auth requirements, quota cost, and caveats in under 1 minute; a power user can discover the selector contract and prepare a valid first request in under 3 minutes; representative valid requests preserve channel section items, empty collections, selected lookup mode, requested parts, endpoint identity, quota context, and any returned continuation details consistently  
**Constraints**: Scope is limited to the single `channelSections_list` Layer 2 tool; preserve near-raw `channelSections.list` semantics; do not add Layer 3 channel layout analysis, playlist item expansion, video metadata expansion, channel analytics, section ranking, layout recommendations, mutation behavior, enrichment, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `1` before invocation; document the current official `hl` deprecation and content-owner authorization caveat; protect API keys, OAuth tokens, stack traces, private channel data, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`channelSections.list`), required `part` selection, exactly one supported selector from `channelId`, `id`, or `mine`, mixed/conditional auth disclosure, official quota cost `1`, successful empty-result handling, current official caveat that `hl` is deprecated, current official content-owner parameter caveat, near-raw channel-section collection results, and focused contract/unit/integration coverage

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

- YT-212 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/contracts/channel-sections-list-tool-contract.md` defines the MCP-facing `channelSections_list` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts and the YT-112 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `channelSections_list` discovery, metadata, schema, selector validation, handler behavior, result mapping, auth error behavior, caveat visibility, and registration.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `channelSections_list` contracts, schema builders, validators, selector helpers, auth-context helpers, handler adapters, response mappers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth/filter/caveat disclosure, safe public metadata, no credential or private-data leakage, reuse of shared request context and error categories, and the one-endpoint scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channel-sections-list-tool-contract.md
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
    │       ├── channel_sections.py
    │       ├── contracts.py
    │       ├── conventions.py
    │       ├── examples.py
    │       └── families.py
    ├── protocol/
    │   └── methods.py
    └── integrations/
        └── resources/
            ├── channel_sections.py
            ├── consumers/
            │   └── channel_sections.py
            ├── validators/
            │   └── channel_sections.py
            └── response_normalizers/
                └── channel_sections.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_channel_sections_contract.py
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_layer1_channel_sections_contract.py
├── integration/
│   ├── test_youtube_channel_sections_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_channel_sections.py
    ├── test_youtube_common_scaffolding.py
    ├── test_list_tools_method.py
    ├── test_method_routing.py
    └── test_layer1_foundation.py
```

**Structure Decision**: Keep YT-212 inside the existing single Python MCP service. Add endpoint-specific behavior through a new channel-sections Layer 2 resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and reuse the existing YT-112 Layer 1 wrapper rather than creating a separate service, persistence layer, selector framework, or monolithic YouTube endpoint module. Export the new public tool through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope for default public registration; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm official `channelSections.list` request facts: quota cost, HTTP method, required `part`, supported selectors, auth-sensitive selectors, deprecated `hl`, content-owner caveat, response shape, and documented errors.
- Confirm how `channelSections_list` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, selector, and error rules.
- Confirm how the existing YT-112 Layer 1 `channelSections.list` wrapper exposes endpoint identity, selector validation, mixed auth, quota cost, caveats, and execution.
- Confirm the minimal public tool registration and discovery path needed for the concrete Layer 2 channel-sections endpoint tool.
- Confirm response handling for successful channel-section collections, empty collections, selected lookup mode, requested parts, safe caveat context, optional returned continuation fields if present, and safe upstream failure categories.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `channelSections.list` documentation for current quota, parameters, response shape, auth notes, deprecation notes, content-owner caveats, and documented errors. Source: https://developers.google.com/youtube/v3/docs/channelSections/list
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` for concrete Layer 2 endpoint patterns established by YT-203 through YT-211.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channel_sections.py` for Layer 1 execution and consumer patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `channelSections.list` metadata, selector, auth, quota, `hl` deprecation, content-owner caveat, optional pagination discrepancy, empty-result, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-212 focused on the concrete `channelSections_list` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `channelSections_list` public MCP tool metadata, input schema expectations, result shape, usage notes, mixed-auth disclosure, quota disclosure, selector guidance, official `hl` deprecation note, content-owner caveat, optional returned continuation handling, empty-result behavior, and availability caveats.
- Model the caller-facing request entities: channel-section lookup filter, part selection, optional compatibility pagination cursor, auth requirement, caveat disclosure, channel-section collection result, quota disclosure, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no playlist item expansion, video metadata expansion, channel analytics, section ranking, layout recommendations, mutation behavior, or higher-level enrichment.
- Provide a quick verification path that proves discovery, valid `id` lookup, valid `channelId` lookup, authorized `mine` lookup, empty results, conflicting-filter rejection, missing-authorization rejection, deprecated `hl` visibility, content-owner caveat visibility, safe error mapping, and default registration.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/contracts/channel-sections-list-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors and existing concrete endpoint tools do not yet provide an executable public `channelSections_list` tool, endpoint-specific schema, handler behavior, registration path, discovery metadata retention, selector validation, mixed-auth behavior, caveat visibility, empty-result behavior, or channel-section result contract.
- **Green**: Produce the data model, `channelSections_list` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Channel Sections Through a Public Tool

- **Red**: Add failing contract/integration checks proving `channelSections_list` is absent from discovery/registration and cannot yet return valid channel-section collection results with endpoint identity, quota cost, selected lookup mode, requested parts, returned items, optional returned continuation fields, and operation context preserved.
- **Green**: Add the minimum public tool definition, schema, handler adapter, registration path, and response mapping needed to call the existing Layer 1 `channelSections.list` capability for supported channel-section lookup requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`.
- **Refactor**: Consolidate list-result response-shape helpers with existing Layer 2 conventions where practical, verify channel-section collection results remain near-raw, confirm reStructuredText docstrings on changed functions, and run focused `channelSections_list` checks.

### User Story 2 - Understand Cost, Access, Filters, and Caveats Before Calling

- **Red**: Add failing discovery/contract checks proving `channelSections_list` metadata, description, and usage notes must expose upstream identity `channelSections.list`, quota cost `1`, mixed/conditional auth, supported selectors `channelId`, `id`, and `mine`, owner-scoped OAuth requirement for `mine`, official `hl` deprecation, content-owner authorization caveat, optional pagination discrepancy, empty-result behavior, and out-of-scope boundaries. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, auth requirement, selector rules, deprecation and content-owner caveats, empty-result handling, optional returned continuation handling, and out-of-scope behavior before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `channelSections_list` metadata is available.
- **Refactor**: Remove duplicated quota/auth/filter wording, keep metadata safe for public discovery, verify no credentials, tokens, stack traces, private channel data, or secret values appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported Channel-Section Requests Clearly

- **Red**: Add failing unit and contract tests for missing `part`, missing selector, empty selector values, multiple selectors, invalid `mine`, unsupported optional fields, unsupported pagination fields if not supported by the final contract, `mine` without OAuth, API-key attempts for owner-scoped lookup, upstream invalid criteria, invalid IDs, missing channel, missing channel section, quota exhaustion, unavailable service, and unexpected upstream failure categories.
- **Green**: Add the minimum selector validation, auth preflight, schema rules, caveat validation, optional pagination compatibility handling, and safe error mapping needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `channelSections_list` tool unless a small shared validator is clearly reusable by later list endpoint slices.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `channelSections.list`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, YT-201/YT-202 representative examples, `activities_list`, captions tools, `channelBanners_insert`, `channels_list`, and `channels_update`.
- Treat `channelSections_list` as one concrete endpoint-backed Layer 2 public tool; do not convert additional representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_channel_sections.py tests/contract/test_youtube_channel_sections_contract.py tests/integration/test_youtube_channel_sections_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper, consumers, validators, or response normalizers: `python3 -m pytest tests/contract/test_layer1_channel_sections_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `channelSections_list` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private channel data, stack traces, and secret values.
- Prefer contract and handler helpers local to `channelSections_list` over broad dispatcher or transport rewrites.
- If official pagination behavior remains absent from current documentation, avoid claiming first-class pagination request support; preserve returned continuation fields only if they appear in Layer 1 or upstream-compatible fixtures.

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

- Feature-local contracts define the MCP-facing `channelSections_list` behavior, including discovery metadata, input schema, result shape, examples, mixed-auth expectations, selector rules, official `hl` deprecation, content-owner caveat, optional returned continuation handling, failure categories, and out-of-scope boundaries.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, and Layer 1 `channelSections.list` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, selector helpers, auth-context helpers, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth/filter/caveat visibility, MCP-safe error categories, no credential or private-data leakage, explicit out-of-scope higher-level channel-section behavior, and a single-endpoint scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
