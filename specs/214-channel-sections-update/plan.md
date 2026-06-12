# Implementation Plan: YT-214 Layer 2 Tool `channelSections_update`

**Branch**: `214-channel-sections-update` | **Date**: 2026-06-12 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the Layer 2 endpoint-backed YouTube public MCP tool, `channelSections_update`, mapped to upstream `channelSections.update`. The technical approach extends the existing channel-sections Layer 2 resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, reuses the YT-114 Layer 1 `channelSections.update` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, and adds only the update-specific public tool contract, handler, OAuth/body validation, discovery metadata, examples, registration, updated-resource mapping, overwrite-sensitive guidance, and tests required for this one low-level channel-section update tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing concrete channel-sections Layer 2 module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`; existing Layer 2 `channels_update` pattern under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` for updated-resource result conventions; existing Layer 1 `channelSections.update` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`; existing Layer 1 channel-sections consumers, validators, and response normalizers under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channel_sections.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, partner-context state, and representative channel-section update results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `channelSections_update` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, body-shape helpers, content-rule helpers, OAuth helpers, partner-context helpers, overwrite-guidance helpers, result mappers, handler adapters, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can identify quota, OAuth, partner-context, part-selection, required target identifier, writable fields, and overwrite-sensitive update behavior in under 2 minutes; a power user can discover `channelSections_update`, choose valid writable fields, and prepare a valid first request in under 3 minutes; representative valid requests preserve returned channel-section resource fields and operation context consistently  
**Constraints**: Scope is limited to the single `channelSections_update` Layer 2 tool; preserve near-raw `channelSections.update` semantics; do not add Layer 3 layout design, multi-section ordering, playlist creation, video metadata expansion, channel analytics, ranking, recommendation, channel branding, bulk editing, enrichment, patch semantics, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `50` before invocation; require eligible OAuth before write attempts; require `body.id` for target section identity; warn that omitted existing properties can be deleted by update behavior; protect API keys, OAuth tokens, stack traces, private channel data, CMS account details, owner identifiers, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`channelSections.update`), required `part` selection, required channel-section `body`, required `body.id`, required `body.snippet.type`, OAuth-required disclosure, optional content-owner delegation parameter, official quota cost `50`, near-raw updated `channelSection` resource result, playlist/channel content-structure validation, overwrite-sensitive update guidance, and focused contract/unit/integration coverage

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

- YT-214 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/contracts/channel-sections-update-tool-contract.md` defines the MCP-facing `channelSections_update` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts and the YT-114 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `channelSections_update` discovery, metadata, schema, OAuth/body validation, `body.id` validation, content-rule behavior, overwrite guidance, handler behavior, update-result mapping, partner-context guidance, and safe error mapping.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `channelSections_update` contracts, schema builders, validators, body helpers, content-rule helpers, OAuth helpers, partner-context helpers, overwrite-guidance helpers, handler adapters, response mappers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth/writable-field disclosure, safe public metadata, no credential or private-data leakage, reuse of shared request context and error categories, and the one-endpoint scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channel-sections-update-tool-contract.md
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

**Structure Decision**: Keep YT-214 inside the existing single Python MCP service. Add update-specific behavior to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` alongside YT-212 `channelSections_list` and YT-213 `channelSections_insert`, and reuse the existing YT-114 Layer 1 wrapper rather than creating a separate service, persistence layer, channel layout subsystem, or monolithic YouTube endpoint module. Export the new public tool through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope for default public registration; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm official `channelSections.update` request facts: quota cost, HTTP method, required `part`, OAuth scopes, required request body, required `body.id`, required `snippet.type`, supported writable fields, update overwrite behavior, partner delegation parameter, response shape, and documented errors.
- Confirm how `channelSections_update` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, mutation-result, partner-context, and error rules.
- Confirm how the existing YT-114 Layer 1 `channelSections.update` wrapper exposes endpoint identity, OAuth auth, quota cost, body validation, content rules, delegation context, and execution.
- Confirm the minimal public tool registration and discovery path needed for the concrete Layer 2 channel-sections update endpoint tool.
- Confirm response handling for successful updated channel-section resources, selected part context, safe partner context, invalid target identity, not-editable sections, missing target sections, overwrite-sensitive requests, and safe upstream failure categories.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `channelSections.update` documentation for current quota, parameters, request body, response shape, OAuth scopes, delegation notes, overwrite behavior, and documented errors. Source: https://developers.google.com/youtube/v3/docs/channelSections/update
- Review official YouTube `channelSections` resource documentation for resource fields, section type behavior, content details, and channel-section limits. Source: https://developers.google.com/youtube/v3/docs/channelSections
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` for concrete Layer 2 endpoint patterns established by YT-209 through YT-213.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channel_sections.py` for Layer 1 execution and consumer patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `channelSections.update` metadata, OAuth, delegation, quota, request body, required `body.id`, part-selection, `snippet.type`, content-rule, overwrite, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-214 focused on the concrete `channelSections_update` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `channelSections_update` public MCP tool metadata, input schema expectations, result shape, usage notes, OAuth disclosure, quota disclosure, part-selection guidance, target identity guidance, partner-context guidance, content-structure rules, overwrite-sensitive update caveat, and availability caveats.
- Model the caller-facing request entities: part selection, target channel-section identifier, writable channel-section body, writable field rule, section content rule, optional partner context, OAuth requirement, updated channel-section resource, quota disclosure, writable-field disclosure, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no section sorting, patch semantics, multi-section replacement, playlist creation, video metadata expansion, analytics, ranking, layout recommendation, channel branding, bulk editing, or higher-level enrichment.
- Provide a quick verification path that proves discovery, valid title/position update, valid playlist-backed update, valid channel-backed update, valid partner-context guidance, updated-resource result mapping, missing-OAuth rejection, missing-part rejection, missing-body rejection, missing-section-id rejection, missing-section-type rejection, invalid writable-field rejection, invalid content-structure rejection, duplicate-reference rejection, missing-target mapping, unsupported option rejection, overwrite guidance, and safe error mapping.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/contracts/channel-sections-update-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors and existing channel-sections list/insert implementations do not yet provide an executable public `channelSections_update` tool, endpoint-specific schema, handler behavior, registration path, discovery metadata retention, OAuth-only behavior, `body.id` validation, section-body validation, content-rule validation, partner-context guidance, overwrite guidance, or updated channel-section result contract.
- **Green**: Produce the data model, `channelSections_update` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Update Channel Sections Through a Public Tool

- **Red**: Add failing contract/integration checks proving `channelSections_update` is absent from discovery/registration and cannot yet return a valid updated channel-section resource with endpoint identity, quota cost, selected parts, target section identity, OAuth context, partner context when present, and operation context preserved.
- **Green**: Add the minimum public tool definition, schema, handler adapter, registration path, and response mapping needed to call the existing Layer 1 `channelSections.update` capability for supported authorized update requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`.
- **Refactor**: Consolidate update-result response-shape helpers with existing Layer 2 conventions where practical, using `channels_update` as the closest updated-resource pattern and `channelSections_insert` as the closest channel-section body-validation pattern. Verify updated channel-section results remain near-raw, confirm reStructuredText docstrings on changed functions, and run focused `channelSections_update` checks.

### User Story 2 - Understand Cost, OAuth, and Writable Fields Before Calling

- **Red**: Add failing discovery/contract checks proving `channelSections_update` metadata, description, and usage notes must expose upstream identity `channelSections.update`, quota cost `50`, OAuth-required auth, supported OAuth scopes or equivalent access expectations, required `part`, required `body`, required `body.id`, required `body.snippet.type`, supported writable fields, optional content-owner delegation parameter, overwrite-sensitive update behavior, and out-of-scope boundaries. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, OAuth requirement, part selection, target identity, request body, writable fields, content structure, delegation caveats, overwrite behavior, result shape, and out-of-scope behavior before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `channelSections_update` metadata is available.
- **Refactor**: Remove duplicated quota/auth/writable-field wording, keep metadata safe for public discovery, verify no credentials, tokens, stack traces, private channel data, CMS account details, owner identifiers, or secret values appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported Update Requests Clearly

- **Red**: Add failing unit and contract tests for missing `part`, unsupported part names, missing `body`, non-object body, missing `body.id`, invalid `body.id`, missing `body.snippet`, missing `body.snippet.type`, missing required `contentDetails`, playlist content for non-playlist types, channel content for non-channel types, missing playlist references, missing channel references, duplicate references, private/missing/unavailable references, missing required titles, invalid positions, too many references, missing OAuth authorization, invalid delegation context, not-editable sections, missing target sections, unsupported body fields, unsupported optional parameters, quota exhaustion, unavailable service, and unexpected upstream failure categories.
- **Green**: Add the minimum OAuth preflight, schema rules, body validation, target identity checks, content-rule checks, delegation checks, overwrite guidance, missing-target mapping, not-editable mapping, and safe error mapping needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `channelSections_update` tool unless a small shared validator is clearly reusable with existing insert behavior.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `channelSections.update`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, YT-201/YT-202 representative examples, `activities_list`, captions tools, `channelBanners_insert`, `channels_list`, `channels_update`, `channelSections_list`, and `channelSections_insert`.
- Treat `channelSections_update` as one concrete endpoint-backed Layer 2 public tool; do not convert additional representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_channel_sections.py tests/contract/test_youtube_channel_sections_contract.py tests/integration/test_youtube_channel_sections_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper, consumers, validators, or response normalizers: `python3 -m pytest tests/contract/test_layer1_channel_sections_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `channelSections_update` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private channel data, CMS account details, owner identifiers, stack traces, and secret values.
- Prefer contract and handler helpers local to `channelSections_update` over broad dispatcher or transport rewrites.
- If official body validation rules overlap substantially with existing `channelSections_insert`, keep shared extraction minimal and local to the channel-sections module until the delete slice proves broader reuse.

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

- Feature-local contracts define the MCP-facing `channelSections_update` behavior, including discovery metadata, input schema, result shape, examples, OAuth/delegation expectations, part selection, target section identity, writable-field expectations, overwrite-sensitive behavior, content-structure rules, failure categories, and out-of-scope boundaries.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, and Layer 1 `channelSections.update` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, body helpers, content-rule helpers, OAuth helpers, partner-context helpers, overwrite-guidance helpers, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth/writable-field visibility, MCP-safe error categories, no credential or private-data leakage, explicit out-of-scope higher-level channel-section behavior, and a single-endpoint scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
