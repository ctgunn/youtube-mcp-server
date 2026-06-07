# Implementation Plan: YT-208 Layer 2 Tool `captions_delete`

**Branch**: `208-captions-delete` | **Date**: 2026-06-07 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the Layer 2 endpoint-backed YouTube public MCP tool, `captions_delete`, mapped to the upstream `captions.delete` operation. The technical approach reuses the existing YT-201/YT-202 shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/` and the existing YT-108 Layer 1 `captions.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`, adding only the endpoint-specific public tool contract, handler, discovery metadata, validation, examples, registration, deletion acknowledgment mapping, and tests required for this one low-level destructive caption tool.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; existing shared Layer 2 contract primitives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `captions.delete` wrapper and resource metadata under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation, handler execution state, deletion acknowledgment descriptors, and representative results remain in memory only  
**Testing**: `python3 -m pytest` for full repository validation; targeted `captions_delete` unit, contract, and integration tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for every new or changed Python function, including public tool builders, validators, handler adapters, deletion-acknowledgment helpers, response normalizers, registration helpers, and test helpers when applicable; feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/contracts/`  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service exposing public endpoint-backed YouTube tools through an internal YouTube integration layer  
**Performance Goals**: A client developer can determine quota, OAuth, caption-track identifier, destructive deletion, and delegation requirements for `captions_delete` in under 1 minute; a power user can discover the required identifier and destructive behavior and prepare a valid first request in under 3 minutes; representative valid requests produce a clear deletion acknowledgment with operation context and no fabricated caption resource data  
**Constraints**: Scope is limited to the single `captions_delete` Layer 2 tool; preserve near-raw `captions.delete` semantics; do not add Layer 3 transcript summarization, caption listing, caption creation, caption update, caption download, deletion undo, recovery, language ranking, enrichment, or heuristic interpretation; do not introduce new persistence, external dependencies, hosted transport changes, or broad dispatcher rewrites; expose official quota cost `50` before invocation; protect API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, and secret values from public metadata, examples, errors, docs, and logs; every changed Python function must keep or add a reStructuredText docstring  
**Scale/Scope**: One public Layer 2 endpoint tool, one upstream operation (`captions.delete`), required caption track `id`, optional `onBehalfOfContentOwner` delegation parameter, OAuth-required disclosure, no request body, successful `204 No Content` deletion acknowledgment, official quota cost `50`, and focused contract/unit/integration coverage

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

- YT-208 is contract-first: `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/contracts/captions-delete-tool-contract.md` defines the MCP-facing `captions_delete` contract before implementation tasks are generated.
- The plan extends existing shared Layer 2 contracts and the YT-108 Layer 1 wrapper rather than creating new architecture.
- Red-Green-Refactor is required in Phase 0, Phase 1, and each Phase 2 user story. Implementation must start with failing checks for missing `captions_delete` discovery, metadata, schema, identifier validation, no-body behavior, handler behavior, deletion acknowledgment mapping, OAuth error behavior, delegation guidance, destructive mutation visibility, not-found mapping, and error mapping.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions for `captions_delete` contracts, schema builders, validators, deletion-result helpers, handler adapters, response mappers, registration helpers, or examples must include reStructuredText docstrings covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
- Security, observability, and simplicity are addressed by pre-invocation quota/auth/deletion/delegation disclosure, safe public metadata, no secret or private caption-content leakage, no fabricated deleted-resource payloads, reuse of shared request context and error categories, and the one-endpoint scope boundary.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── captions-delete-tool-contract.md
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

**Structure Decision**: Keep YT-208 inside the existing single Python MCP service. Add endpoint-specific behavior through the shared YouTube Layer 2 tool surfaces and the existing captions Layer 1 wrapper rather than creating a separate service, persistence layer, deletion queue, audit store, or monolithic YouTube endpoint module. The concrete captions public tool should live alongside the current captions Layer 2 code in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` and export through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is in scope if default public registration or discovery metadata must change; `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` is in scope only if MCP-level `tools/list` or `tools/call` error/result mapping must expose the new tool correctly.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the official `captions.delete` request contract: required `id`, optional `onBehalfOfContentOwner`, quota cost, request-body prohibition, OAuth scopes, success response, and documented error cases.
- Confirm how `captions_delete` should build on YT-201/YT-202 shared Layer 2 contracts without duplicating broad metadata, naming, response-boundary, mutation-acknowledgment, and error rules.
- Confirm how the existing YT-108 Layer 1 `captions.delete` wrapper exposes endpoint identity, OAuth auth, quota cost, delegation context, no-body behavior, and execution.
- Confirm the minimal public tool registration and discovery path needed for the next concrete Layer 2 captions endpoint tool.
- Confirm response handling for successful `204 No Content`, safe operation context, deleted caption track id, delegation context, destructive mutation disclosure, and safe upstream failure categories.
- Confirm Python docstring and full-suite verification obligations from the constitution for new or changed public tool functions.

### Research Tasks

- Review official YouTube `captions.delete` documentation for current quota, parameters, no-body requirement, HTTP `204 No Content` success response, OAuth scopes, delegated content-owner notes, and documented errors. Source: https://developers.google.com/youtube/v3/docs/captions/delete
- Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/` for dependency contracts.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` for shared Layer 2 primitives.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` for concrete Layer 2 endpoint patterns established by YT-203 through YT-207.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/captions.py` for Layer 1 execution and consumer patterns.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` for current coverage and gaps.

### Phase 0 Red-Green-Refactor

- **Red**: Capture unresolved `captions.delete` metadata, identifier, OAuth, delegation, quota, no-body request, `204 No Content` result, destructive mutation, registration, error, docstring, and verification decisions as research topics before task generation.
- **Green**: Resolve each topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/research.md` with concrete decisions, rationale, and alternatives considered.
- **Refactor**: Remove duplicated YT-201/YT-202 standards prose from research notes and keep YT-208 focused on the concrete `captions_delete` endpoint tool.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact `captions_delete` public MCP tool metadata, input schema expectations, result shape, usage notes, OAuth disclosure, quota disclosure, required caption-track identifier, delegation guidance, destructive deletion caveat, no-body request rule, `204 No Content` acknowledgment behavior, and availability caveats.
- Model the caller-facing request entities: caption track identifier, optional delegation context, OAuth/permission requirement, deletion acknowledgment result, quota disclosure, destructive mutation disclosure, and error outcome.
- Preserve the Layer 2 boundary: endpoint-backed, near-raw, one upstream operation, no transcript summarization, deletion undo, recovery, language ranking, enrichment, or cross-endpoint composition.
- Provide a quick verification path that proves discovery, valid deletion, valid delegated deletion, deletion acknowledgment results, missing-identifier rejection, invalid-identifier rejection, unsupported-option rejection, OAuth-sensitive rejection, not-found mapping, delegation guidance, and safe error mapping.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/contracts/captions-delete-tool-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where current YT-201/YT-202 representative descriptors and existing captions tools do not yet provide an executable public `captions_delete` tool, endpoint-specific schema, handler behavior, registration path, discovery metadata retention, OAuth-only behavior, no-body validation, or deletion acknowledgment result contract.
- **Green**: Produce the data model, `captions_delete` contract, and quickstart artifacts with enough specificity to drive `/speckit.tasks` and implementation.
- **Refactor**: Re-check that the design stays contract-first, endpoint-scoped, near-raw, secure, observable, simple, and docstring-aware.

## Phase 2: Implementation Strategy

### User Story 1 - Delete Caption Tracks Through a Public Tool

- **Red**: Add failing contract/integration checks proving `captions_delete` is absent from discovery/registration and cannot yet return a valid deletion acknowledgment result with endpoint identity, quota cost, required caption track `id`, destructive mutation outcome, no-body success context, and no fabricated caption resource data.
- **Green**: Add the minimum public tool definition, schema, handler adapter, registration path, and response mapping needed to call the existing Layer 1 `captions.delete` capability for supported authorized caption deletion requests. The default implementation target is `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- **Refactor**: Consolidate deletion acknowledgment response-shape helpers with existing Layer 2 conventions, verify the result remains near-raw and safely represented, confirm reStructuredText docstrings on changed functions, and run focused `captions_delete` checks.

### User Story 2 - Understand Cost, Authorization, and Delegation Before Calling

- **Red**: Add failing discovery/contract checks proving `captions_delete` metadata, description, and usage notes must expose upstream identity `captions.delete`, quota cost `50`, OAuth-required auth, required `id`, optional `onBehalfOfContentOwner` delegation guidance, destructive deletion behavior, no request body, and `204 No Content` success acknowledgment. Include a failing check if dispatcher discovery must preserve metadata beyond `name`, `description`, and `inputSchema`.
- **Green**: Add the minimum metadata and examples needed for callers to inspect cost, permission, identifier, destructive deletion, delegation caveats, no-body behavior, and acknowledgment behavior before invocation. If required by the public contract, extend dispatcher descriptors additively so existing tools keep their current discovery shape while `captions_delete` metadata is available.
- **Refactor**: Remove duplicated quota/auth/delete/delegation wording, keep metadata safe for public discovery, verify no credentials, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or secret values appear in examples/errors/logs, and run focused metadata checks.

### User Story 3 - Reject Unsupported Caption Delete Requests Clearly

- **Red**: Add failing unit and contract tests for missing `id`, blank `id`, malformed identifier values, unsupported extra fields or request body input, missing OAuth authorization, invalid delegation context, insufficient delete permission, upstream `captionNotFound`, upstream `forbidden`, quota exhaustion, unavailable service, and unexpected upstream failure categories.
- **Green**: Add the minimum identifier validation, OAuth preflight, schema rules, no-body rules, delegation checks, permission guidance, not-found mapping, forbidden mapping, quota mapping, and safe error mapping needed to reject unsupported requests with stable caller-facing feedback. Prefer endpoint-specific validation in the concrete `captions_delete` tool unless a small shared validator is clearly reusable by later mutation-acknowledgment endpoint slices.
- **Refactor**: Reuse shared error categories and validation conventions where practical, avoid special-case complexity beyond `captions.delete`, and run focused validation/error tests.

### Regression Strategy

- Preserve existing baseline tools, retrieval tools, dispatcher behavior, MCP transport behavior, Layer 1 wrapper contracts, YT-201/YT-202 representative examples, `activities_list`, `captions_list`, `captions_insert`, `captions_update`, and `captions_download`.
- Treat `captions_delete` as one concrete endpoint-backed Layer 2 public tool; do not convert additional representative descriptors into executable tools beyond this endpoint.
- Use targeted tests before full validation: `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`.
- If default tool discovery or MCP routing changes, also run `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`.
- Include Layer 1 guard checks when implementation touches the existing wrapper: `python3 -m pytest tests/contract/test_layer1_captions_contract.py tests/unit/test_layer1_foundation.py`.
- Complete final validation with `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Rollback and Mitigation

- Keep changes additive to the public tool catalog so rollback can remove `captions_delete` registration and endpoint-specific tests without changing shared contracts for future slices.
- Reuse existing Layer 1 execution and shared Layer 2 metadata/convention helpers to avoid a second upstream request stack.
- Keep examples and tests free of real credentials, tokens, private video data, raw private caption content, binary payloads, signed URLs, deleted-resource internals, and secret values.
- Prefer contract and handler helpers local to `captions_delete` over broad dispatcher or transport rewrites.

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

- Feature-local contracts define the MCP-facing `captions_delete` behavior, including discovery metadata, input schema, result shape, examples, OAuth/delegation expectations, destructive mutation expectations, no-body expectations, `204 No Content` acknowledgment behavior, and failure categories.
- No constitution exceptions are required because the plan uses the existing Python MCP service, shared Layer 2 modules, and Layer 1 `captions.delete` wrapper without adding infrastructure, persistence, or transport changes.
- Red-Green-Refactor is represented in Phase 0, Phase 1, and each Phase 2 user story, with implementation beginning from failing tests and ending with targeted, full-suite, and lint verification.
- reStructuredText docstrings are required for every new or changed Python function, including schema builders, validators, deletion-result helpers, handler adapters, response mappers, registration helpers, and examples.
- Security, observability, and simplicity are addressed by safe public metadata, quota/auth/deletion/delegation visibility, MCP-safe error categories, no secret or private caption-content leakage, no fabricated deletion resource payload, and a single-endpoint scope boundary.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
