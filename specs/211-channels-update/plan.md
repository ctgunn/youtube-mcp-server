# Implementation Plan: YT-211 Layer 2 Tool `channels_update`

**Branch**: `211-channels-update` | **Date**: 2026-06-09 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the Layer 2 endpoint-backed YouTube public MCP tool, `channels_update`, mapped to upstream `channels.update`. The technical approach extends the existing channels resource-family Layer 2 module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, reuses the YT-111 Layer 1 `channels.update` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`, and adds only the endpoint-specific public tool contract, handler, OAuth preflight, writable-part validation, discovery metadata, examples, registration, updated-channel result mapping, and tests required for this one low-level channel mutation tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing channels Layer 2 resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`; existing Layer 1 `channels.update` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`; existing Layer 1 channels validators and response normalizers under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channels.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, authorization context, update body context, and representative updated-channel results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `channels_update` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, writable-part helpers, auth-context helpers, result mappers, handler adapters, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can identify the `channels_update` OAuth requirement, 50-unit quota cost, supported writable parts, read-only exclusions, and part-to-body alignment rule in under 1 minute; a power user can discover the mutation contract and prepare a valid first request in under 3 minutes; representative valid requests preserve updated channel resource content, source operation identity, selected writable part, quota context, and request context consistently  
**Constraints**: Scope is limited to the single `channels_update` Layer 2 tool; preserve near-raw `channels.update` semantics; require OAuth and do not permit public-only updates; support the existing YT-111 writable boundary of `brandingSettings` and `localizations`; do not add Layer 3 channel management, channel lookup, analytics, search ranking, video expansion, playlist expansion, banner upload, bulk channel operations, enrichment, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `50` before invocation; protect API keys, OAuth tokens, stack traces, private channel data, request bodies with sensitive values, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`channels.update`), required `part`, required channel resource `body`, eligible OAuth authorization, supported writable parts `brandingSettings` and `localizations`, official quota cost `50`, updated channel resource result mapping, safe mutation failure categories, official content-owner delegation caveat documented as out of scope for this slice unless YT-111 is expanded first, and focused contract/unit/integration coverage

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

- YT-211 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/contracts/channels-update-tool-contract.md` defines the MCP-facing `channels_update` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts, the existing channels Layer 2 module, and the YT-111 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `channels_update` discovery, metadata, schema, OAuth preflight, writable-part validation, handler behavior, result mapping, banner-boundary notes, safe errors, and registration.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `channels_update` contracts, schema builders, validators, writable-part helpers, auth-context helpers, handler adapters, response mappers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth/writable-part disclosure, safe public metadata, no credential or private-data leakage, reuse of shared request context and error categories, and the one-endpoint mutation scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-update-tool-contract.md
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
            ├── validators/
            │   └── channels.py
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

**Structure Decision**: Keep YT-211 inside the existing single Python MCP service. Add endpoint-specific behavior to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` next to `channels_list` and reuse the existing YT-111 Layer 1 wrapper rather than creating a separate service, persistence layer, mutation framework, or monolithic YouTube endpoint module. Export the new public tool through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope for default public registration; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm official `channels.update` request facts: quota cost, HTTP method, required `part`, OAuth scopes, writable-part limitations, request body requirements, content-owner delegation caveat, response shape, overwrite semantics, and documented errors.
- Confirm how `channels_update` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, mutation, and error rules.
- Confirm how the existing YT-111 Layer 1 `channels.update` wrapper exposes endpoint identity, OAuth-required auth, quota cost, supported writable parts, request validators, and execution.
- Confirm the minimal public tool registration and discovery path needed for the concrete Layer 2 channels update endpoint tool.
- Confirm response handling for successful updated channel resources, selected writable part, request context, quota context, safe upstream failure categories, and no automatic banner upload or multi-step channel-management behavior.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `channels.update` documentation for current quota, parameters, authorization scopes, writable parts, request body, response shape, overwrite warning, content-owner caveats, and documented errors. Source: https://developers.google.com/youtube/v3/docs/channels/update
- Review official YouTube quota calculator for the current `channels.update` official quota-unit cost. Source: https://developers.google.com/youtube/v3/determine_quota_cost
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` for concrete Layer 2 endpoint patterns established by YT-203 through YT-210.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/channels.py` for Layer 1 execution and validation patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `channels.update` metadata, auth, writable-part, body-alignment, content-owner delegation caveat, overwrite warning, result mapping, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-211 focused on the concrete `channels_update` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `channels_update` public MCP tool metadata, input schema expectations, result shape, usage notes, OAuth disclosure, quota disclosure, writable-part guidance, overwrite warning, banner-boundary note, and availability caveats.
- Model the caller-facing request entities: writable part, channel body, access context, updated channel result, quota disclosure, writable boundary disclosure, official content-owner delegation caveat, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no channel lookup, no analytics, no ranking, no video or playlist expansion, no banner upload, and no multi-step channel-management orchestration.
- Provide a quick verification path that proves discovery, valid `brandingSettings` update, valid `localizations` update, banner URL activation update, missing OAuth rejection, missing body rejection, unsupported part rejection, part-to-body mismatch rejection, read-only field rejection, safe upstream error mapping, and default registration.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/contracts/channels-update-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors and existing concrete channels endpoint tools do not yet provide an executable public `channels_update` tool, endpoint-specific schema, handler behavior, OAuth-only auth context, registration path, discovery metadata retention, writable-part validation, updated-resource result mapping, overwrite warning, or safe mutation error contract.
- **Green**: Produce the data model, `channels_update` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Update Supported Channel Settings Through a Public Tool

- **Red**: Add failing contract/integration checks proving `channels_update` is absent from discovery/registration and cannot yet return valid updated channel results with endpoint identity, quota cost, selected writable part, requested body context, source operation, and operation context preserved.
- **Green**: Add the minimum public tool definition, schema, handler adapter, OAuth auth context, registration path, and response mapping needed to call the existing Layer 1 `channels.update` capability for supported channel update requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`.
- **Refactor**: Consolidate mutation-result response-shape helpers with existing Layer 2 conventions where practical, verify updated channel results remain near-raw, confirm reStructuredText docstrings on changed functions, and run focused `channels_update` checks.

### User Story 2 - Understand Cost, Access, and Writable Boundaries Before Calling

- **Red**: Add failing discovery/contract checks proving `channels_update` metadata, description, and usage notes must expose upstream identity `channels.update`, quota cost `50`, `oauth_required` auth, supported writable parts `brandingSettings` and `localizations`, read-only exclusions, part-to-body alignment, one-part update guidance, overwrite warning, content-owner delegation as an official-doc caveat outside this slice, banner URL activation boundary, and out-of-scope channel-management workflows. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, auth requirement, writable-part rules, body alignment, overwrite behavior, banner boundary, and out-of-scope behavior before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `channels_update` metadata is available.
- **Refactor**: Remove duplicated quota/auth/writable-part wording, keep metadata safe for public discovery, verify no credentials, tokens, stack traces, private channel data, sensitive body values, or secret values appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported or Ineligible Channel Updates Clearly

- **Red**: Add failing unit and contract tests for missing `part`, empty `part`, multiple writable parts, missing `body`, empty `body`, missing `body.id`, unsupported parts, part-to-body mismatch, read-only fields, unexpected top-level fields, missing OAuth, ineligible channel-management access, upstream branding/localization validation failures, quota exhaustion, unavailable service, and unexpected upstream failure categories.
- **Green**: Add the minimum writable-part validation, body validation, OAuth preflight, schema rules, safe error mapping, and handler failure translation needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `channels_update` tool unless a small shared mutation validator is clearly reusable by later update endpoint slices.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `channels.update`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, YT-201/YT-202 representative examples, `activities_list`, captions tools, `channelBanners_insert`, and `channels_list`.
- Treat `channels_update` as one concrete endpoint-backed Layer 2 public tool; do not convert additional representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_channels.py tests/contract/test_youtube_channels_contract.py tests/integration/test_youtube_channels_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper, validators, consumers, or response normalizers: `python3 -m pytest tests/contract/test_layer1_channels_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `channels_update` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private channel data, stack traces, sensitive channel body values, and secret values.
- Prefer contract and handler helpers local to `channels_update` over broad dispatcher or transport rewrites.
- If official writable-part behavior is expanded beyond the current YT-111 wrapper boundary, record that as a deliberate follow-up or dependency update rather than silently broadening YT-211 implementation scope.

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

- Feature-local contracts define the MCP-facing `channels_update` behavior, including discovery metadata, input schema, result shape, examples, OAuth expectations, writable-part rules, body-alignment rules, overwrite warning, banner boundary, failure categories, and out-of-scope boundaries.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, existing channels resource-family module, and Layer 1 `channels.update` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, writable-part helpers, auth-context helpers, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth/writable-part visibility, MCP-safe error categories, no credential or private-data leakage, explicit out-of-scope higher-level channel behavior, and a single-endpoint mutation scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
