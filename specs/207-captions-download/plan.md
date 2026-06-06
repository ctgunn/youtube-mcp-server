# Implementation Plan: YT-207 Layer 2 Tool `captions_download`

**Branch**: `207-captions-download` | **Date**: 2026-06-02 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the Layer 2 endpoint-backed YouTube public MCP tool, `captions_download`, mapped to the upstream `captions.download` operation. The technical approach reuses the existing YT-201/YT-202 shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/` and the existing YT-107 Layer 1 `captions.download` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`, adding only the endpoint-specific public tool contract, handler, discovery metadata, validation, examples, registration, and tests required for this one low-level caption-content download tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `captions.download` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, safe content descriptors, and representative results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `captions_download` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, handler adapters, content-result helpers, response normalizers, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can determine quota, permission, caption-track identifier, `tfmt`, and `tlang` requirements for `captions_download` in under 1 minute; a power user can discover the required identifier and optional conversion contract and prepare a valid first request in under 3 minutes; representative valid requests preserve downloaded-content form and operation context consistently  
**Constraints**: Scope is limited to the single `captions_download` Layer 2 tool; preserve near-raw `captions.download` semantics; do not add Layer 3 transcript summarization, caption listing, caption creation, caption update, caption deletion, language ranking, enrichment, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `200` before invocation; protect API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`captions.download`), required caption track `id`, optional `tfmt` values `sbv`, `scc`, `srt`, `ttml`, and `vtt`, optional `tlang` ISO 639-1 language code, optional `onBehalfOfContentOwner` delegation parameter, OAuth-required disclosure, permission-to-edit disclosure, binary downloaded-content result with `application/octet-stream` response context, and focused contract/unit/integration coverage

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

- YT-207 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/contracts/captions-download-tool-contract.md` defines the MCP-facing `captions_download` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts and the YT-107 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `captions_download` discovery, metadata, schema, identifier validation, `tfmt` validation, `tlang` validation, handler behavior, downloaded-content mapping, OAuth error behavior, delegation guidance, conversion failure mapping, and error mapping.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `captions_download` contracts, schema builders, validators, content-result helpers, handler adapters, response normalizers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth/permission/conversion disclosure, safe public metadata, no secret or private caption-content leakage, reuse of shared request context and error categories, and the one-endpoint scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── captions-download-tool-contract.md
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
    │       ├── contracts.py
    │       ├── conventions.py
    │       ├── examples.py
    │       └── families.py
    ├── protocol/
    │   └── methods.py
    └── integrations/
        └── resources/
            ├── captions.py
            └── consumers/
                └── captions.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_captions_contract.py
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_layer1_captions_contract.py
├── integration/
│   ├── test_youtube_captions_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_captions.py
    ├── test_youtube_common_scaffolding.py
    ├── test_list_tools_method.py
    ├── test_method_routing.py
    └── test_layer1_foundation.py
```

**Structure Decision**: Keep YT-207 inside the existing single Python MCP service. Add endpoint-specific behavior through the shared YouTube Layer 2 tool surfaces and the existing captions Layer 1 wrapper rather than creating a separate service, persistence layer, binary storage subsystem, or monolithic YouTube endpoint module. The concrete captions public tool should live alongside the current captions Layer 2 code in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` and export through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope if default public registration or discovery metadata must change; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the official `captions.download` request contract: required `id`, optional `onBehalfOfContentOwner`, optional `tfmt`, optional `tlang`, quota cost, response form, OAuth scopes, permission-to-edit requirement, and documented error cases.
- Confirm how `captions_download` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, conversion-option, downloaded-content, and error rules.
- Confirm how the existing YT-107 Layer 1 `captions.download` wrapper exposes endpoint identity, OAuth auth, quota cost, delegation context, option validation, and execution.
- Confirm the minimal public tool registration and discovery path needed for the next concrete Layer 2 endpoint tool.
- Confirm response handling for successful downloaded caption content, safe operation context, output-format indicators, target-language indicators, content-type/file-form indicators, and safe upstream failure categories.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `captions.download` documentation for current quota, parameters, response shape, OAuth scopes, permission-to-edit note, delegation notes, supported `tfmt` values, `tlang` behavior, and documented errors.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` for concrete Layer 2 endpoint patterns established by YT-203 through YT-206.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/captions.py` for Layer 1 execution and consumer patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `captions.download` metadata, identifier, output-format, target-language, OAuth, delegation, quota, binary response, permission, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-207 focused on the concrete `captions_download` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `captions_download` public MCP tool metadata, input schema expectations, result shape, usage notes, OAuth disclosure, quota disclosure, required caption-track identifier, supported `tfmt` values, `tlang` guidance, delegation guidance, permission-to-edit caveat, binary result behavior, and availability caveats.
- Model the caller-facing request entities: caption track identifier, output format option, target language option, optional delegation context, OAuth/permission requirement, downloaded caption content result, quota disclosure, conversion disclosure, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no transcript summarization, language ranking, enrichment, or cross-endpoint composition.
- Provide a quick verification path that proves discovery, valid default downloads, valid format-specific downloads, valid target-language downloads, downloaded-content results, missing-identifier rejection, unsupported-format rejection, unsupported-language rejection, OAuth-sensitive rejection, conversion-failure mapping, delegation guidance, and safe error mapping.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/contracts/captions-download-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors do not yet provide an executable public `captions_download` tool, endpoint-specific schema, handler behavior, registration path, discovery metadata retention, `tfmt`/`tlang` validation, OAuth-only behavior, or downloaded-content result contract.
- **Green**: Produce the data model, `captions_download` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Download Caption Track Content Through a Public Tool

- **Red**: Add failing contract/integration checks proving `captions_download` is absent from discovery/registration and cannot yet return a valid downloaded caption content result with operation context, required `id`, requested `tfmt`/`tlang` when supplied, content-form indicators, and returned payload characteristics preserved.
- **Green**: Add the minimum public tool definition, schema, handler adapter, registration path, and response mapping needed to call the existing Layer 1 `captions.download` capability for supported authorized default, format-specific, and target-language download requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- **Refactor**: Consolidate downloaded-content response-shape helpers with existing Layer 2 conventions, verify caption content remains near-raw and safely represented, confirm reStructuredText docstrings on changed functions, and run focused `captions_download` checks.

### User Story 2 - Understand Cost, Permissions, and Conversion Options Before Calling

- **Red**: Add failing discovery/contract checks proving `captions_download` metadata, description, and usage notes must expose upstream identity `captions.download`, quota cost `200`, OAuth-required auth, permission-to-edit caveat, required `id`, optional `tfmt` values `sbv`, `scc`, `srt`, `ttml`, and `vtt`, optional `tlang` ISO 639-1 guidance, optional delegation guidance, and binary response context. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, permission, identifier, format conversion, language conversion, delegation caveats, and binary-result behavior before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `captions_download` metadata is available.
- **Refactor**: Remove duplicated quota/auth/download/conversion wording, keep metadata safe for public discovery, verify no credentials, stack traces, signed URLs, raw private caption content, binary payloads, or secret values appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported Caption Download Requests Clearly

- **Red**: Add failing unit and contract tests for missing `id`, blank `id`, unsupported `tfmt`, malformed `tlang`, missing OAuth authorization, invalid delegation context, insufficient download permission, upstream `couldNotConvert`, upstream `captionNotFound`, upstream `forbidden`, quota exhaustion, unavailable service, and unexpected upstream failure categories.
- **Green**: Add the minimum identifier validation, `tfmt` validation, `tlang` validation, OAuth preflight, schema rules, delegation checks, permission guidance, conversion-failure mapping, not-found mapping, and safe error mapping needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `captions_download` tool unless a small shared validator is clearly reusable by later download-like endpoint slices.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `captions.download`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, YT-201/YT-202 representative examples, `activities_list`, `captions_list`, `captions_insert`, and `captions_update`.
- Treat `captions_download` as one concrete endpoint-backed Layer 2 public tool; do not convert additional representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper: `python3 -m pytest tests/contract/test_layer1_captions_contract.py tests/unit/test_layer1_foundation.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `captions_download` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private video data, raw private caption content, binary payloads, signed URLs, and secret values.
- Prefer contract and handler helpers local to `captions_download` over broad dispatcher or transport rewrites.

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

- Feature-local contracts define the MCP-facing `captions_download` behavior, including discovery metadata, input schema, result shape, examples, OAuth/delegation expectations, permission expectations, `tfmt` expectations, `tlang` expectations, binary-content context, and failure categories.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, and Layer 1 `captions.download` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, content-result helpers, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth/permission/conversion visibility, MCP-safe error categories, no secret or private caption-content leakage, and a single-endpoint scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
