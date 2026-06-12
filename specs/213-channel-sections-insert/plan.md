# Implementation Plan: YT-213 Layer 2 Tool `channelSections_insert`

**Branch**: `213-channel-sections-insert` | **Date**: 2026-06-11 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the Layer 2 endpoint-backed YouTube public MCP tool, `channelSections_insert`, mapped to upstream `channelSections.insert`. The technical approach extends the existing channel-sections Layer 2 resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, reuses the YT-113 Layer 1 `channelSections.insert` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, and adds only the insert-specific public tool contract, handler, OAuth/body validation, discovery metadata, examples, registration, create-result mapping, and tests required for this one low-level channel-section creation tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing concrete channel-sections Layer 2 module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`; existing Layer 1 `channelSections.insert` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`; existing Layer 1 channel-sections consumers, validators, and response normalizers under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channel_sections.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, partner-context state, and representative channel-section create results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `channelSections_insert` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, body-shape helpers, content-rule helpers, OAuth helpers, partner-context helpers, result mappers, handler adapters, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can identify quota, OAuth, partner-context, part-selection, and channel-section body requirements in under 2 minutes; a power user can discover `channelSections_insert`, choose a valid section type and content structure, and prepare a valid first request in under 3 minutes; representative valid requests preserve returned channel-section resource fields and operation context consistently  
**Constraints**: Scope is limited to the single `channelSections_insert` Layer 2 tool; preserve near-raw `channelSections.insert` semantics; do not add Layer 3 layout design, section ordering automation, playlist creation, video metadata expansion, channel analytics, ranking, recommendation, channel branding, bulk editing, enrichment, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `50` before invocation; require eligible OAuth before write attempts; protect API keys, OAuth tokens, stack traces, private channel data, CMS account details, owner identifiers, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`channelSections.insert`), required `part` selection, required channel-section `body`, required `body.snippet.type`, OAuth-required disclosure, optional content-owner/channel delegation parameters, official quota cost `50`, near-raw created `channelSection` resource result, official maximum of 10 channel sections, playlist/channel content-structure validation, and focused contract/unit/integration coverage

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

- YT-213 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/contracts/channel-sections-insert-tool-contract.md` defines the MCP-facing `channelSections_insert` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts and the YT-113 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `channelSections_insert` discovery, metadata, schema, OAuth/body validation, content-rule behavior, handler behavior, create-result mapping, partner-context guidance, capacity guidance, and safe error mapping.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `channelSections_insert` contracts, schema builders, validators, body helpers, content-rule helpers, OAuth helpers, partner-context helpers, handler adapters, response mappers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth/content disclosure, safe public metadata, no credential or private-data leakage, reuse of shared request context and error categories, and the one-endpoint scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channel-sections-insert-tool-contract.md
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

**Structure Decision**: Keep YT-213 inside the existing single Python MCP service. Add insert-specific behavior to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` alongside YT-212 `channelSections_list`, and reuse the existing YT-113 Layer 1 wrapper rather than creating a separate service, persistence layer, channel layout subsystem, or monolithic YouTube endpoint module. Export the new public tool through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope for default public registration; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm official `channelSections.insert` request facts: quota cost, HTTP method, required `part`, OAuth scopes, required request body, required `snippet.type`, supported writable fields, partner delegation parameters, response shape, capacity limit, and documented errors.
- Confirm how `channelSections_insert` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, mutation-result, partner-context, and error rules.
- Confirm how the existing YT-113 Layer 1 `channelSections.insert` wrapper exposes endpoint identity, OAuth auth, quota cost, body validation, content rules, delegation context, and execution.
- Confirm the minimal public tool registration and discovery path needed for the concrete Layer 2 channel-sections insert endpoint tool.
- Confirm response handling for successful created channel-section resources, selected part context, safe partner context, capacity and content-rule failures, and safe upstream failure categories.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `channelSections.insert` documentation for current quota, parameters, request body, response shape, OAuth scopes, delegation notes, resource limits, and documented errors. Source: https://developers.google.com/youtube/v3/docs/channelSections/insert
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` for concrete Layer 2 endpoint patterns established by YT-209 through YT-212.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channel_sections.py` for Layer 1 execution and consumer patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `channelSections.insert` metadata, OAuth, delegation, quota, request body, part-selection, `snippet.type`, content-rule, capacity, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-213 focused on the concrete `channelSections_insert` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `channelSections_insert` public MCP tool metadata, input schema expectations, result shape, usage notes, OAuth disclosure, quota disclosure, part-selection guidance, partner-context guidance, content-structure rules, section limit caveat, and availability caveats.
- Model the caller-facing request entities: part selection, channel-section body, section content rule, optional partner or delegated-channel context, OAuth requirement, created channel-section resource, quota disclosure, content-structure disclosure, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no section sorting, section replacement, playlist creation, video metadata expansion, analytics, ranking, layout recommendation, channel branding, bulk editing, or higher-level enrichment.
- Provide a quick verification path that proves discovery, valid playlist-backed creation, valid channel-backed creation, valid partner-context guidance, created-resource result mapping, missing-OAuth rejection, missing-part rejection, missing-body rejection, missing-section-type rejection, invalid content-structure rejection, duplicate-reference rejection, capacity-limit mapping, unsupported option rejection, and safe error mapping.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/contracts/channel-sections-insert-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors and existing channel-sections list implementation do not yet provide an executable public `channelSections_insert` tool, endpoint-specific schema, handler behavior, registration path, discovery metadata retention, OAuth-only behavior, section-body validation, content-rule validation, partner-context guidance, or created channel-section result contract.
- **Green**: Produce the data model, `channelSections_insert` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Create Channel Sections Through a Public Tool

- **Red**: Add failing contract/integration checks proving `channelSections_insert` is absent from discovery/registration and cannot yet return a valid created channel-section resource with endpoint identity, quota cost, selected parts, OAuth context, partner context when present, and operation context preserved.
- **Green**: Add the minimum public tool definition, schema, handler adapter, registration path, and response mapping needed to call the existing Layer 1 `channelSections.insert` capability for supported authorized create requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`.
- **Refactor**: Consolidate create-result response-shape helpers with existing Layer 2 conventions where practical, verify created channel-section results remain near-raw, confirm reStructuredText docstrings on changed functions, and run focused `channelSections_insert` checks.

### User Story 2 - Understand Cost, OAuth, and Content Rules Before Calling

- **Red**: Add failing discovery/contract checks proving `channelSections_insert` metadata, description, and usage notes must expose upstream identity `channelSections.insert`, quota cost `50`, OAuth-required auth, supported OAuth scopes or equivalent access expectations, required `part`, required `body`, required `body.snippet.type`, supported writable fields, optional content-owner/channel delegation parameters, maximum section limit, section-type-specific content rules, and out-of-scope boundaries. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, OAuth requirement, part selection, request body, content structure, delegation caveats, capacity caveat, result shape, and out-of-scope behavior before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `channelSections_insert` metadata is available.
- **Refactor**: Remove duplicated quota/auth/content wording, keep metadata safe for public discovery, verify no credentials, tokens, stack traces, private channel data, CMS account details, owner identifiers, or secret values appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported Create Requests Clearly

- **Red**: Add failing unit and contract tests for missing `part`, unsupported part names, missing `body`, non-object body, missing `body.snippet`, missing `body.snippet.type`, missing required `contentDetails`, playlist content for non-playlist types, channel content for non-channel types, missing playlist references, missing channel references, duplicate references, private/missing/unavailable references, missing required titles, invalid positions, too many references, missing OAuth authorization, invalid delegation context, section capacity failures, unsupported body fields, unsupported optional parameters, quota exhaustion, unavailable service, and unexpected upstream failure categories.
- **Green**: Add the minimum OAuth preflight, schema rules, body validation, content-rule checks, delegation checks, capacity guidance, and safe error mapping needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `channelSections_insert` tool unless a small shared validator is clearly reusable by later channel-section update/delete slices.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `channelSections.insert`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, YT-201/YT-202 representative examples, `activities_list`, captions tools, `channelBanners_insert`, `channels_list`, `channels_update`, and `channelSections_list`.
- Treat `channelSections_insert` as one concrete endpoint-backed Layer 2 public tool; do not convert additional representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_channel_sections.py tests/contract/test_youtube_channel_sections_contract.py tests/integration/test_youtube_channel_sections_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper, consumers, validators, or response normalizers: `python3 -m pytest tests/contract/test_layer1_channel_sections_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `channelSections_insert` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private channel data, CMS account details, owner identifiers, stack traces, and secret values.
- Prefer contract and handler helpers local to `channelSections_insert` over broad dispatcher or transport rewrites.
- If official body validation rules overlap substantially with `channelSections.update`, keep shared extraction minimal and local to the channel-sections module until later slices prove broader reuse.

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

- Feature-local contracts define the MCP-facing `channelSections_insert` behavior, including discovery metadata, input schema, result shape, examples, OAuth/delegation expectations, part selection, section-body expectations, content-structure rules, maximum-section caveat, failure categories, and out-of-scope boundaries.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, and Layer 1 `channelSections.insert` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, body helpers, content-rule helpers, OAuth helpers, partner-context helpers, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth/content visibility, MCP-safe error categories, no credential or private-data leakage, explicit out-of-scope higher-level channel-section behavior, and a single-endpoint scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
