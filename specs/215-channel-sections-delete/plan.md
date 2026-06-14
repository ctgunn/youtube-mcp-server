# Implementation Plan: Layer 2 Tool `channelSections_delete`

**Branch**: `215-channel-sections-delete` | **Date**: 2026-06-14 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `channelSections_delete` for the upstream YouTube Data API `channelSections.delete` endpoint. The implementation will extend the existing channel-sections Layer 2 resource-family module, reuse the existing Layer 1 `build_channel_sections_delete_wrapper()` from YT-115, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth, response boundaries, deletion acknowledgment, safe errors, examples, and registry integration.

The tool remains endpoint-backed and destructive: it accepts exactly one required channel-section `id`, optional partner-only `onBehalfOfContentOwner`, requires eligible OAuth authorization, costs 50 official quota units per call, rejects unsupported workflow options, and maps successful deletion to a clear acknowledgment without fabricating deleted channel-section resource fields.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; Layer 1 `channelSections.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, deletion acknowledgment, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including helper validators, handler builders, result mappers, default executor/transport helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single deletion request performs one Layer 1 wrapper call and constant-time local validation; no additional lookup, bulk, retry orchestration, playlist cleanup, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, require OAuth, expose quota cost 50 in metadata/description/examples, reject unsupported request fields before execution, avoid leaking owner IDs/tokens/secrets in results or errors, keep implementation colocated with existing channel-section Layer 2 module patterns  
**Scale/Scope**: One public MCP tool (`channelSections_delete`), one Layer 2 resource-family extension, focused contract/unit/integration coverage, and documentation artifacts for YT-215 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `channelSections_delete` contract builder, descriptor builder, handler builder, argument validator, result mapper, auth-context helper, upstream-error mapper, local default transport/executor helpers, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for no request body, missing/invalid `id`, unsupported options, missing OAuth, partner context safety, missing-resource mapping, and no fabricated deleted resource fields.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
specs/215-channel-sections-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channelSections_delete.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
src/mcp_server/
├── integrations/resources/
│   └── channel_sections.py          # Existing Layer 1 delete wrapper dependency from YT-115
├── tools/
│   ├── dispatcher.py                # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py              # Public exports for channelSections_delete symbols
│       ├── channel_sections.py      # Layer 2 contract, schema, examples, handler, validation, result mapping
│       ├── contracts.py             # Existing shared contract primitives
│       └── examples.py              # Representative shared contract set

tests/
├── contract/
│   ├── test_youtube_channel_sections_contract.py
│   └── test_youtube_common_contract.py
├── integration/
│   └── test_youtube_channel_sections_registration.py
└── unit/
    ├── test_youtube_channel_sections.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Extend the existing concrete channel-sections Layer 2 module rather than introducing a new package. This preserves the YT-201 resource-family convention already used by `channelSections_list`, `channelSections_insert`, and `channelSections_update`.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official `channelSections.delete` request, quota, OAuth scopes, parameters, request-body policy, response behavior, partner-context behavior, and documented error categories.
- Confirm existing YT-115 Layer 1 wrapper availability and request-shape assumptions.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example conventions in the local codebase.
- Compare existing deletion tools, especially `captions_delete`, with existing channel-section `list`/`insert`/`update` tools to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/data-model.md)
- [contracts/channelSections_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/contracts/channelSections_delete.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, docstring requirements, safe error/result surfaces, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Delete Channel Sections Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `channelSections_delete` is absent until implemented, requires `id`, invokes the Layer 1 delete wrapper once with OAuth context, and maps success to an acknowledgment result with endpoint, quota cost, deletion outcome, target ID, and safe partner flags.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local no-body transport, default executor, public exports, and dispatcher registration needed for successful authorized deletes.

**Refactor**: Align naming, docstrings, helper reuse, and error mapping with existing channel-section tools and deletion tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Deletion Risk Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-only auth mode, destructive-delete caveats, no request body, optional partner context, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized deletion, partner context, validation failures, repeated/missing resource, and auth failure.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific caveats reviewable in `channel_sections.py`.

### User Story 3 - Reject Unsupported Delete Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing OAuth, missing/empty/non-string `id`, unsupported body/part/bulk/recovery/layout/playlist options, empty partner context, missing target section, authorization failure, quota failure, endpoint unavailable, deprecated endpoint, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure owner IDs, tokens, stack traces, and raw details are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, and `tests/integration/test_youtube_channel_sections_registration.py`.

**Green**: Export `CHANNEL_SECTIONS_DELETE_*` symbols, add `build_channel_sections_delete_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `channel_sections.py` cohesive and avoid changes to unrelated resource families.

## Risk and Mitigation

- **Official response caveat**: Current official documentation says success returns a `channelSection` resource, while the feature spec also requires no-body success handling. The implementation should support and preserve any returned upstream fields but treat no-body deletion as a valid acknowledgment without fabricating fields.
- **Destructive operation risk**: Metadata, usage notes, examples, and result shape must state that the tool deletes the target section and does not support undo, recovery, layout repair, playlist cleanup, or bulk delete.
- **Security risk**: Partner owner identifiers and OAuth/token details must be accepted only as inputs, forwarded safely to Layer 1, and represented in results/errors only as boolean context flags.
- **Scope risk**: Do not add lookup-before-delete, section sorting, playlist deletion, recovery, analytics, or higher-level layout editing.

## Verification Commands

```bash
pytest tests/contract/test_youtube_channel_sections_contract.py tests/unit/test_youtube_channel_sections.py tests/integration/test_youtube_channel_sections_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py
pytest
ruff check .
```
