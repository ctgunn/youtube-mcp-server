# Implementation Plan: YT-210 Layer 2 Tool `channels_list`

**Branch**: `210-channels-list` | **Date**: 2026-06-08 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the Layer 2 endpoint-backed YouTube public MCP tool, `channels_list`, mapped to upstream `channels.list`. The technical approach reuses the existing YT-201/YT-202 shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/` and the existing YT-110 Layer 1 `channels.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`, adding only the endpoint-specific public tool contract, handler, discovery metadata, validation, examples, registration, channel collection result mapping, and tests required for this one low-level channel lookup tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `channels.list` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`; existing Layer 1 consumers and response normalizers under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channels.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, selector context, and representative channel collection results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `channels_list` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, selector helpers, auth-context helpers, result mappers, handler adapters, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can identify supported `channels_list` lookup modes and access requirements in under 1 minute; a power user can discover the selector and pagination contract and prepare a valid first request in under 3 minutes; representative valid requests preserve channel items, empty collections, selected lookup mode, requested parts, and pagination details consistently  
**Constraints**: Scope is limited to the single `channels_list` Layer 2 tool; preserve near-raw `channels.list` semantics; do not add Layer 3 channel analytics, channel search ranking, video expansion, playlist expansion, branding updates, bulk channel operations, enrichment, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `1` before invocation; protect API keys, OAuth tokens, stack traces, private channel data, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`channels.list`), selector validation for `id`, `mine`, `forHandle`, and `forUsername`, required `part` selection, optional `pageToken` and `maxResults`, mixed/conditional auth disclosure, official quota cost `1`, successful empty-result handling, near-raw channel collection results, and focused contract/unit/integration coverage

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

- YT-210 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/contracts/channels-list-tool-contract.md` defines the MCP-facing `channels_list` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts and the YT-110 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `channels_list` discovery, metadata, schema, selector validation, handler behavior, result mapping, auth error behavior, pagination visibility, empty-result handling, and error mapping.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `channels_list` contracts, schema builders, validators, selector helpers, auth-context helpers, handler adapters, response mappers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth/filter disclosure, safe public metadata, no credential or private-data leakage, reuse of shared request context and error categories, and the one-endpoint scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-list-tool-contract.md
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
    │       ├── captions.py
    │       ├── channel_banners.py
    │       ├── channels.py
    │       ├── contracts.py
    │       ├── conventions.py
    │       ├── examples.py
    │       └── families.py
    ├── protocol/
    │   └── methods.py
    └── integrations/
        └── resources/
            ├── channels.py
            ├── consumers/
            │   └── channels.py
            └── response_normalizers/
                └── channels.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_channels_contract.py
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_layer1_channels_contract.py
├── integration/
│   ├── test_youtube_channels_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_channels.py
    ├── test_youtube_common_scaffolding.py
    ├── test_list_tools_method.py
    ├── test_method_routing.py
    └── test_layer1_foundation.py
```

**Structure Decision**: Keep YT-210 inside the existing single Python MCP service. Add endpoint-specific behavior through a new channel Layer 2 resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and the existing YT-110 Layer 1 wrapper rather than creating a separate service, persistence layer, selector framework, or monolithic YouTube endpoint module. Export the new public tool through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope for default public registration; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm official `channels.list` request facts: quota cost, HTTP method, required `part`, supported selectors, pagination, auth-sensitive selectors, content-owner constraints, response shape, and documented errors.
- Confirm how `channels_list` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, selector, and error rules.
- Confirm how the existing YT-110 Layer 1 `channels.list` wrapper exposes endpoint identity, selector validation, mixed auth, quota cost, and execution.
- Confirm the minimal public tool registration and discovery path needed for the concrete Layer 2 channels endpoint tool.
- Confirm response handling for successful channel collections, empty collections, pagination tokens, selected lookup mode, requested parts, and safe upstream failure categories.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `channels.list` documentation for current quota, parameters, response shape, auth notes, content-owner caveats, and documented errors. Source: https://developers.google.com/youtube/v3/docs/channels/list
- Review official YouTube channel implementation guidance for retrieving channels by `mine`, `id`, `forHandle`, and `forUsername`. Source: https://developers.google.com/youtube/v3/guides/implementation/channels
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py` for concrete Layer 2 endpoint patterns established by YT-203 through YT-209.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channels.py` for Layer 1 execution and consumer patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `channels.list` metadata, selector, auth, pagination, quota, empty-result, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-210 focused on the concrete `channels_list` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `channels_list` public MCP tool metadata, input schema expectations, result shape, usage notes, mixed-auth disclosure, quota disclosure, selector guidance, pagination behavior, empty-result behavior, and availability caveats.
- Model the caller-facing request entities: channel lookup filter, part selection, pagination cursor, auth requirement, channel collection result, quota disclosure, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no search ranking, analytics, video expansion, playlist expansion, branding updates, or higher-level enrichment.
- Provide a quick verification path that proves discovery, valid `id` lookup, valid `forHandle` lookup, valid `forUsername` lookup, authorized `mine` lookup, pagination, empty results, conflicting-filter rejection, missing-authorization rejection, and safe error mapping.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/contracts/channels-list-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors and existing concrete endpoint tools do not yet provide an executable public `channels_list` tool, endpoint-specific schema, handler behavior, registration path, discovery metadata retention, selector validation, mixed-auth behavior, pagination, or empty-result contract.
- **Green**: Produce the data model, `channels_list` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve Channels Through a Public Tool

- **Red**: Add failing contract/integration checks proving `channels_list` is absent from discovery/registration and cannot yet return valid channel collection results with endpoint identity, quota cost, selected lookup mode, requested parts, pagination fields, and operation context preserved.
- **Green**: Add the minimum public tool definition, schema, handler adapter, registration path, and response mapping needed to call the existing Layer 1 `channels.list` capability for supported channel lookup requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`.
- **Refactor**: Consolidate list-result response-shape helpers with existing Layer 2 conventions, verify channel collection results remain near-raw, confirm reStructuredText docstrings on changed functions, and run focused `channels_list` checks.

### User Story 2 - Understand Cost, Access, and Filter Rules Before Calling

- **Red**: Add failing discovery/contract checks proving `channels_list` metadata, description, and usage notes must expose upstream identity `channels.list`, quota cost `1`, mixed/conditional auth, supported selectors `id`, `mine`, `forHandle`, and `forUsername`, owner-scoped OAuth requirement for `mine`, pagination fields, empty-result behavior, and availability caveats. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, auth requirement, selector rules, pagination behavior, empty-result handling, and out-of-scope boundaries before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `channels_list` metadata is available.
- **Refactor**: Remove duplicated quota/auth/filter wording, keep metadata safe for public discovery, verify no credentials, tokens, stack traces, private channel data, or secret values appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported Channel Lookup Requests Clearly

- **Red**: Add failing unit and contract tests for missing `part`, missing selector, empty selector values, multiple selectors, malformed `forHandle`, invalid `maxResults`, unsupported optional fields, `mine` without OAuth, API-key attempts for owner-scoped lookup, upstream invalid criteria, quota exhaustion, unavailable service, and unexpected upstream failure categories.
- **Green**: Add the minimum selector validation, auth preflight, schema rules, pagination bounds, and safe error mapping needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `channels_list` tool unless a small shared validator is clearly reusable by later list endpoint slices.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `channels.list`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, YT-201/YT-202 representative examples, `activities_list`, `captions_list`, `captions_insert`, `captions_update`, `captions_download`, `captions_delete`, and `channelBanners_insert`.
- Treat `channels_list` as one concrete endpoint-backed Layer 2 public tool; do not convert additional representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_channels.py tests/contract/test_youtube_channels_contract.py tests/integration/test_youtube_channels_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper, consumers, or response normalizers: `python3 -m pytest tests/contract/test_layer1_channels_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `channels_list` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private channel data, stack traces, and secret values.
- Prefer contract and handler helpers local to `channels_list` over broad dispatcher or transport rewrites.

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

- Feature-local contracts define the MCP-facing `channels_list` behavior, including discovery metadata, input schema, result shape, examples, mixed-auth expectations, selector rules, pagination, empty-result behavior, failure categories, and out-of-scope boundaries.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, and Layer 1 `channels.list` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, selector helpers, auth-context helpers, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth/filter visibility, MCP-safe error categories, no credential or private-data leakage, explicit out-of-scope higher-level channel behavior, and a single-endpoint scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
