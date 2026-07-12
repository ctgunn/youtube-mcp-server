# Implementation Plan: Layer 2 Tool `playlists_delete`

**Branch**: `239-playlists-delete` | **Date**: 2026-07-12 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlists_delete` for the YouTube endpoint operation `playlists.delete`. The implementation will extend the existing playlists Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`, reuse the existing Layer 1 `build_playlists_delete_wrapper()` from YT-139, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth disclosure, destructive request validation, deletion acknowledgment shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires one target playlist `id`, costs 50 official quota units per call, requires OAuth-backed user authorization, returns a deletion acknowledgment with safe target context, documents that successful calls delete user-visible playlists, and does not add playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, restore, rollback, idempotency guarantees, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 playlists module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`; existing Layer 1 `playlists.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlists.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, deletion acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlists delete contract builders, descriptor builders, handler builders, argument validators, OAuth-context helpers, deletion acknowledgment mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist delete request performs one Layer 1 wrapper call and constant-time local validation; no playlist traversal, playlist item traversal, image retrieval, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, restore lookup, rollback workflow, or cross-endpoint expansion is introduced  
**Constraints**: Preserve destructive endpoint semantics, expose quota cost 50 in metadata/description/examples, declare OAuth requirement, require one `id`, reject unsupported request fields before execution, avoid leaking credential material or raw diagnostics in results or errors, add delete code under the existing `youtube_common` playlists family structure, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`playlists_delete`), additive changes to the existing playlists Layer 2 resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-239 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-139 wrapper and YT-239 seed agree on quota cost `50`, OAuth-required access, required `id`, unsupported modifier rejection, destructive no-body acknowledgment behavior, repeat-delete caveat, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlists_delete` contract builder, descriptor builder, handler builder, argument validator, OAuth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `id`, blank or non-string `id`, unsupported optional fields, unsupported modifiers, missing OAuth, insufficient authorization, quota failures, upstream invalid requests, missing-resource or already-deleted outcomes, endpoint unavailable, deprecated endpoint behavior, destructive no-body success, repeat-delete caveat visibility, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlists_delete.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlists.py          # Existing Layer 1 delete wrapper dependency from YT-139
├── tools/
│   ├── dispatcher.py         # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py       # Public exports for playlists_delete symbols
│       ├── contracts.py      # Existing shared contract primitives
│       ├── examples.py       # Representative shared contract set, if catalog export requires update
│       ├── families.py       # Existing playlists family placement metadata
│       └── playlists.py      # Existing Layer 2 playlists family; add delete contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `playlists.py` Layer 2 family module because YT-236/YT-237/YT-238 already established the public playlists family, the Layer 1 dependency lives under the same resource-family name, and this slice should remain separate from playlist items, playlist images, thumbnails, search, transcripts, and higher-level workflow modules. This keeps `playlists_delete` cohesive with `playlists_list`, `playlists_insert`, and `playlists_update` while avoiding a broad refactor.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlists.delete` quota, OAuth mode, required `id`, unsupported modifier boundary, destructive response shape, repeat-delete caveat, and documented error categories.
- Confirm existing YT-139 Layer 1 wrapper availability and whether the public YT-239 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, mutation acknowledgment, error, availability, and example conventions in the local codebase.
- Compare existing delete and mutation tools, especially `playlistItems_delete`, `playlistImages_delete`, `comments_delete`, `channelSections_delete`, `captions_delete`, `playlists_insert`, and `playlists_update`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported identifier shape, OAuth handling, registration surface, destructive acknowledgment shape, safe error categories, examples, repeat-delete caveat, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, restore, rollback, idempotency guarantees, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/data-model.md)
- [contracts/playlists_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/contracts/playlists_delete.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, destructive acknowledgment result shape, OAuth and quota caveats, target identity validation, unsupported modifier rejection, no-body success behavior, repeat-delete caveat, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlists_delete`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required access disclosure, quota accuracy, target identity validation, destructive acknowledgment behavior, repeat-delete caveat visibility, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Delete Playlists Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlists_delete` is absent until implemented, requires `id`, invokes the Layer 1 delete wrapper once with OAuth-required auth, and maps success to a deletion acknowledgment result with endpoint, quota cost 50, target identifier context, auth context, and mutation outcome.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, OAuth-backed default local executor, public exports, and dispatcher registration needed for successful OAuth-backed playlist deletion.

**Refactor**: Align naming, docstrings, helper reuse, destructive caveats, repeat-delete caveat, and error mapping with `playlistItems_delete`, `playlistImages_delete`, `comments_delete`, `channelSections_delete`, `captions_delete`, and existing playlists mutation conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Deletion Impact Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required auth disclosure, required identifier, destructive response boundary, no-body acknowledgment behavior, repeat-delete caveat, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful OAuth-backed deletion, successful no-body deletion acknowledgment, missing identifier, malformed identifier, unsupported input, missing authorization, insufficient authorization, missing-resource or already-deleted failure, quota or upstream service failure, repeat-delete caveat, and out-of-scope playlist-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific identifier, quota, OAuth, destructive, no-body acknowledgment, repeat-delete, and unsupported-input guidance reviewable in `playlists.py`.

### User Story 3 - Reject Invalid or Unauthorized Deletion Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, blank `id`, non-string `id`, unsupported body/part/playlist metadata/paging/listing inputs, unsupported modifiers, missing OAuth access, authorization failure, quota failure, missing resource or already-deleted target, endpoint unavailable, deprecated endpoint behavior, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, API keys, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlists_contract.py`, `tests/integration/test_youtube_playlists_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLISTS_DELETE_*` symbols, add `build_playlists_delete_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlists.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist items, playlist images, thumbnails, search, captions/transcripts, analytics, recommendations, restore/rollback workflows, or higher-level workflow modules.

## Risk and Mitigation

- **Destructive action risk**: The tool deletes a user-visible playlist. Metadata, usage notes, examples, quickstart, and result context must make the destructive nature visible before invocation.
- **OAuth risk**: Playlist deletion requires eligible OAuth-backed user authorization. The handler must reject missing or insufficient OAuth before execution and must not expose tokens in results, errors, logs, or examples.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Acknowledgment ambiguity risk**: Successful delete may not return a deleted resource body. The result mapper must provide explicit deletion acknowledgment with target identifier context without fabricating resource fields.
- **Target identity risk**: The request must clearly identify one playlist to delete; missing or conflicting target identity must fail locally instead of becoming an ambiguous upstream mutation.
- **Repeat-delete risk**: Retrying deletion after an unclear outcome can produce a missing-resource response if the first request succeeded. The public contract must document that this tool does not add restore, rollback, or idempotency guarantees.
- **Upstream rejection risk**: A valid local request can still fail due to playlist ownership, missing playlist, unwritable target state, quota, or service availability. Error mapping must keep these distinct from local validation failures.
- **Scope risk**: Do not add playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, restore, rollback, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose OAuth tokens, API keys, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlists_delete` should live in the existing `playlists` Layer 2 module, not in playlist items, playlist images, thumbnails, search, captions, transcripts, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
