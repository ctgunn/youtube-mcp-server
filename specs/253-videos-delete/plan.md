# Implementation Plan: Layer 2 Tool `videos_delete`

**Branch**: `253-videos-delete` | **Date**: 2026-07-24 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videos_delete` for the YouTube endpoint operation `videos.delete`. The implementation will extend the existing videos Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, reuse the existing Layer 1 `build_videos_delete_wrapper()` from YT-153, and follow YT-201/YT-202 shared contract conventions for naming, 50-unit quota disclosure, OAuth-only access disclosure, destructive-action guidance, no-body target-only validation, no-content deletion acknowledgment result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and mutation-oriented: it requires exactly one target video `id`, requires OAuth for every request, rejects request bodies, partner delegation, bulk delete shapes, unsupported modifiers, aliases, and out-of-scope workflow fields before execution, acknowledges successful no-content delete operations, and does not add listing, metadata lookup, metadata update, upload, rating, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, recovery, policy review, or higher-level content-management behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing videos Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`; existing Layer 1 `videos.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, deletion acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including videos delete contract builders, descriptor builders, handler builders, argument validators, target-context helpers, OAuth-context helpers, deletion acknowledgment result mappers, upstream-error mappers, local default executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single delete invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 50-unit quota cost, OAuth requirement, required `id`, destructive-action semantics, no-content acknowledgment result shape, and out-of-scope boundaries in under 2 minutes; no lookup, update, upload, rating, abuse reporting, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, media transfer, recovery, or multi-endpoint workflow is introduced  
**Constraints**: Preserve endpoint delete semantics, expose quota cost 50 in metadata/description/examples, require OAuth-only access, require exactly one non-empty target video `id`, send no request body, reject `body`, `onBehalfOfContentOwner`, bulk delete shapes, aliases, and unsupported fields unless a narrow Layer 1 contract expansion is approved during implementation, map success to an acknowledgment rather than a refreshed video resource or recovery state, avoid leaking API keys, OAuth tokens, authorization details, raw upstream diagnostics, stack traces, sensitive access context, or secret-bearing details in results or errors, keep changes under the videos Layer 2 family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videos_delete`), endpoint-specific additions to the existing videos Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-253 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-153 wrapper dependency, YT-253 seed requirements, shared Layer 2 contracts, and existing videos module pattern into one endpoint-specific `videos_delete` plan with quota cost `50`, OAuth-only access, required `id`, no request body, no partner delegation in this slice, safe no-content deletion acknowledgment result shaping, and distinct validation/access/permission/quota/not-found/policy/upstream-refusal behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videos_delete` contract builder, descriptor builder, handler builder, argument validator, target-context helper, auth-context helper, acknowledgment result mapper, upstream-error mapper, local default executor, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `id`, blank or non-string `id`, comma-separated or duplicate target values where locally detectable, supplied `body`, unsupported top-level fields, rejected `onBehalfOfContentOwner`, missing OAuth, API-key-only access, insufficient permission, forbidden or policy failure, not-found failure, quota failure, endpoint unavailable, deprecated endpoint behavior, no-content success shaping, out-of-scope lookup/update/upload/rating/abuse-report/caption/thumbnail/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment/recovery requests, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos_delete.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── videos.py                       # Existing Layer 1 delete wrapper dependency from YT-153
├── tools/
│   ├── dispatcher.py                   # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                 # Public exports for videos_delete symbols
│       ├── contracts.py                # Existing shared contract primitives
│       ├── conventions.py              # Existing response/error boundary helpers
│       ├── examples.py                 # Representative shared contract set; add concrete videos_delete contract if needed
│       ├── families.py                 # Existing videos family placement metadata
│       └── videos.py                   # Existing Layer 2 family; add delete contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_youtube_videos_contract.py
├── integration/
│   ├── test_youtube_tool_registration.py
│   └── test_youtube_videos_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_videos.py
```

**Structure Decision**: Extend the existing `videos.py` Layer 2 resource-family module because YT-247 through YT-252 established videos family placement, YT-153 provides the matching Layer 1 resource wrapper, and YT-253 should remain separate from listing, insert/update, rating lookup/mutation, abuse reporting, video abuse reason lookup, search, captions, thumbnails, playlists, comments, analytics, recommendations, and higher-level workflows. This keeps the public tool cohesive with the upstream `videos` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local YT-253 seed requirements: public `videos_delete` tool, official quota cost `50`, and clear OAuth documentation.
- Confirm existing YT-153 Layer 1 wrapper availability and whether the public YT-253 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, mutation-result, and example conventions in the local codebase.
- Confirm current videos Layer 2 family placement and how to add `videos_delete` beside `videos_list`, `videos_insert`, `videos_update`, `videos_rate`, `videos_getRating`, and `videos_reportAbuse` in the existing `youtube_common/videos.py` module.
- Confirm how to add any representative `videos_delete` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing destructive mutation tools, especially `playlistImages_delete`, `subscriptions_delete`, `comments_delete`, `playlists_delete`, `playlistItems_delete`, and the YT-153 Layer 1 acknowledgment behavior, to choose the smallest consistent acknowledgment shape.

**Red**: Identify missing planning facts that would block task generation, including supported request shape, OAuth handling, videos family placement, registration surface, acknowledgment result shape, safe error categories, examples, no-content rules, unsupported field rejection, partner-delegation boundary, destructive-action caveats, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into video lookup, update, upload, rating, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, recovery, policy review, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/data-model.md)
- [contracts/videos_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/contracts/videos_delete.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, target-only delete request contract, deletion acknowledgment result shape, OAuth and quota caveats, `id` validation, rejected body and partner delegation, unsupported modifier rejection, destructive-action guidance, safe error categories, and no lookup/update/upload/rating/abuse-report/analytics/recovery/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videos_delete`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, target-only request boundaries, no-content acknowledgment behavior, no partner-delegation expansion in this slice, destructive-action guidance, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Delete a Video Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `videos_delete` is absent until implemented, requires `id`, rejects `body` and unsupported modifiers, invokes the Layer 1 delete wrapper once with OAuth context, and maps no-content success to a deletion acknowledgment with endpoint, quota cost 50, target video identity, access context, availability state, destructive-action context, and mutation details.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, target helper, auth-context helper, acknowledgment mapper, default local no-content executor, public exports, and dispatcher registration needed for successful video deletion.

**Refactor**: Align naming, docstrings, helper reuse, acknowledgment mapping, and error mapping with existing Layer 2 mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Quota, OAuth, and Destructive Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `id`, no request body, no-content acknowledgment result shape, rejected `onBehalfOfContentOwner`, destructive-action guidance, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful authorized deletion, missing target validation failure, malformed target failure, unsupported modifier failure, supplied body failure, rejected partner delegation, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable target failure, and out-of-scope workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required `id`, no-body rule, no-content acknowledgment behavior, destructive-action semantics, partner-delegation boundary, and unsupported-input guidance reviewable in `videos.py`.

### User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Delete Requests Clearly

**Red**: Add failing validation and error-mapping checks for non-object arguments, missing `id`, blank or non-string `id`, duplicate or comma-separated target values where locally detectable, supplied `body`, unsupported top-level fields, supplied `onBehalfOfContentOwner`, lookup fields, update fields, upload fields, rating fields, abuse-report fields, caption fields, thumbnail fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, recovery fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, forbidden or policy failure, not-found failure, deprecated behavior, no-content success, upstream refusal, conflict behavior where observable, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, target context extraction, acknowledgment context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, authorization headers, sensitive authorization details, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the official endpoint request shape.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_videos_contract.py`, `tests/integration/test_youtube_videos_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEOS_DELETE_*` symbols, import and use `build_videos_delete_wrapper()`, add `build_videos_delete_tool_descriptor()` to the default registry, and add representative contract/example coverage while preserving the public tool name `videos_delete`.

**Refactor**: Keep `videos.py` cohesive, keep Layer 1 changes narrow, and avoid changes to search, captions, video abuse report reasons, video categories, thumbnails, playlists, comments, rating lookup/mutation, report-abuse, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Destructive mutation risk**: Video deletion removes user content from the caller's perspective. Validation must require explicit target video identity before execution, and examples must use test-safe identifiers.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Access risk**: Video deletion is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, or credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **No-body boundary risk**: The public tool accepts only `id` in this slice. Request bodies, unsupported fields, aliases, partner delegation, and bulk delete shapes must be rejected or left unexposed until the Layer 1 contract is deliberately expanded.
- **No-content result risk**: Successful `videos.delete` returns no refreshed video resource. Result mapping must provide a useful acknowledgment without fabricating video metadata, recovery state, analytics, recommendations, rankings, summaries, or enrichment.
- **Policy-refusal risk**: A valid request can still be refused due to ownership, permissions, policy state, video availability, deletion eligibility, quota state, or service constraints. These outcomes must remain distinct from local validation failures and successful acknowledgments.
- **Scope risk**: Do not add listing, metadata lookup, metadata update, upload, rating lookup/mutation, abuse reporting, video abuse reason lookup, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, recovery, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `videos_delete` should live in the existing videos Layer 2 module, not in search, captions, thumbnails, playlists, comments, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
