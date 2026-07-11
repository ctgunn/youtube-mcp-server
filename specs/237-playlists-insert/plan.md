# Implementation Plan: Layer 2 Tool `playlists_insert`

**Branch**: `237-playlists-insert` | **Date**: 2026-07-10 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlists_insert` for the YouTube Data API `playlists.insert` endpoint. The implementation will extend the existing playlists Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`, reuse the existing Layer 1 `build_playlists_insert_wrapper()` from YT-137, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth disclosure, writable request validation, near-raw mutation result shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires `part` plus `body.snippet.title`, costs 50 official quota units per call, requires OAuth-backed user authorization, returns the created playlist resource with safe request context, documents that successful calls create user-visible playlists, and does not add playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, duplicate-prevention, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 playlists module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`; existing Layer 1 `playlists.insert` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlists.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, created playlist results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlists insert contract builders, descriptor builders, handler builders, argument validators, OAuth-context helpers, mutation result mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist insert request performs one Layer 1 wrapper call and local validation proportional to supplied part and body fields; no playlist item traversal, image retrieval, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, duplicate lookup, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 50 in metadata/description/examples, declare OAuth requirement, require `part` and minimum writable `body.snippet.title`, reject unsupported request fields before execution, avoid leaking credential material or raw diagnostics in results or errors, add insert code under the existing `youtube_common` playlists family structure, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`playlists_insert`), additive changes to the existing playlists Layer 2 resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-237 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-137 wrapper and YT-237 seed agree on quota cost `50`, OAuth-required access, required `part`, minimum `body.snippet.title` writable payload, unsupported optional write fields unless deliberately expanded, mutation result behavior, duplicate-create caveat, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlists_insert` contract builder, descriptor builder, handler builder, argument validator, OAuth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, missing `body`, missing `body.snippet.title`, malformed body, unsupported optional write fields, unsupported modifiers, missing OAuth, quota failures, upstream invalid requests, forbidden create outcomes, endpoint unavailable, mutation result shaping, duplicate-create caveat visibility, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlists_insert.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlists.py          # Existing Layer 1 insert wrapper dependency from YT-137
├── tools/
│   ├── dispatcher.py         # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py       # Public exports for playlists_insert symbols
│       ├── contracts.py      # Existing shared contract primitives
│       ├── examples.py       # Representative shared contract set, if catalog export requires update
│       ├── families.py       # Existing playlists family placement metadata
│       └── playlists.py      # Existing Layer 2 playlists family; add insert contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_playlists_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_playlists_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_playlists.py
```

**Structure Decision**: Extend the existing `playlists.py` Layer 2 family module because YT-236 already established the public playlists family, the Layer 1 dependency lives under the same resource-family name, and this slice should remain separate from playlist items, playlist images, thumbnails, search, transcripts, and higher-level workflow modules. This keeps `playlists_insert` cohesive with `playlists_list` while avoiding a broad refactor.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlists.insert` quota, OAuth mode, required `part`, required writable body, minimum title requirement, supported optional write boundary, mutation response shape, and documented error categories.
- Confirm existing YT-137 Layer 1 wrapper availability and whether the public YT-237 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, access, mutation result, error, availability, and example conventions in the local codebase.
- Compare existing mutation tools, especially `playlistItems_insert`, `playlistImages_insert`, `channelSections_insert`, `comments_insert`, and the shared resource-family registry, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported writable shape, OAuth handling, registration surface, mutation result shape, safe error categories, examples, mutation-warning text, duplicate-create caveat, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, duplicate-prevention, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/data-model.md)
- [contracts/playlists_insert.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/contracts/playlists_insert.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/237-playlists-insert/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, mutation result shape, OAuth and quota caveats, part validation, writable body validation, unsupported modifier rejection, mutation warning, duplicate-create caveat, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlists_insert`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth disclosure, quota accuracy, part and writable body validation, mutation result behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Create Playlists Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlists_insert` is absent until implemented, requires `part` plus `body.snippet.title`, requires OAuth-backed access, invokes the Layer 1 insert wrapper once, and maps success to a created playlist result with endpoint, quota cost 50, requested part context, safe creation context, OAuth context, and returned playlist fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local insert transport, default executor, public exports, and dispatcher registration needed for successful playlist creation.

**Refactor**: Align naming, docstrings, helper reuse, mutation caveats, OAuth handling, and error mapping with `playlistItems_insert`, `playlistImages_insert`, `channelSections_insert`, `comments_insert`, and shared mutation-result conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Create Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth requirement, required part selection, required `body.snippet.title`, supported optional writable details, created-resource result shape, mutation warning, duplicate-create caveat, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful playlist creation, creation with supported optional details if supported by the chosen contract, missing part, invalid part, missing body, missing title, malformed writable detail, unsupported modifier, missing authorization, upstream create failure, and out-of-scope playlist-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, writable body, mutation warning, duplicate-create caveat, and unsupported-input guidance reviewable in `playlists.py`.

### User Story 3 - Reject Invalid or Unauthorized Playlist Creation Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, unsupported `part`, missing `body`, non-object `body`, missing `body.snippet`, missing or blank `body.snippet.title`, unsupported write fields, unsupported modifiers, missing OAuth, quota failure, forbidden create failure, endpoint unavailable, upstream invalid request, deprecated behavior, and unexpected upstream failure.

**Green**: Implement validator, OAuth-context selection, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlists_contract.py`, `tests/integration/test_youtube_playlists_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLISTS_INSERT_*` symbols, add `build_playlists_insert_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlists.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist items, playlist images, thumbnails, search, captions/transcripts, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Mutation safety risk**: Successful calls create user-visible playlists. Metadata, usage notes, examples, quickstart, and result context must make mutation behavior visible before invocation.
- **OAuth risk**: Playlist creation requires eligible OAuth-backed user authorization. The handler must reject missing or insufficient OAuth before execution and must not expose tokens in results, errors, logs, or examples.
- **Writable boundary risk**: The current Layer 1 wrapper supports the minimum `body.snippet.title` write path and rejects unsupported optional write fields unless deliberately expanded. Validation must keep this boundary clear and testable.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Duplicate-create risk**: Retrying a creation call after an unclear outcome may create another playlist. The public contract must document that this tool does not add idempotency or duplicate-prevention behavior.
- **Scope risk**: Do not add playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, duplicate lookup, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlists_insert` should live in the existing `playlists` Layer 2 module, not in playlist items, playlist images, search, captions, transcripts, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
