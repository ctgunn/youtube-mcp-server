# Implementation Plan: Layer 2 Tool `watermarks_unset`

**Branch**: `255-watermarks-unset` | **Date**: 2026-07-27 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `watermarks_unset` for the YouTube endpoint operation `watermarks.unset`. The implementation will extend the existing Layer 2 watermarks resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`, reuse the existing Layer 1 `build_watermarks_unset_wrapper()` from YT-155, and follow YT-201/YT-202 shared contract conventions for naming, 50-unit quota disclosure, OAuth-only access disclosure, no-upload guidance, channel-context validation, safe mutation acknowledgment result shaping, safe errors, examples, public exports, representative catalog alignment, and default registry integration.

The tool remains endpoint-backed and mutation-oriented: it requires exactly one target `channelId`; requires OAuth for every request; rejects `body`, `media`, watermark-setting payloads, partner delegation, bulk request shapes, aliases, and out-of-scope workflow fields before execution; acknowledges successful sparse or no-content watermark-unset operations; distinguishes no-removal-possible outcomes from successful removals; and does not add watermark upload, watermark placement updates, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflow, or higher-level research behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing watermarks Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`; existing Layer 1 `watermarks.unset` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, watermark-removal acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including watermarks unset contract builders, descriptor builders, handler builders, argument validators, channel-context helpers, OAuth-context helpers, acknowledgment result mappers, upstream-error mappers, local default executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single watermark-unset invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 50-unit quota cost, OAuth requirement, required `channelId`, no-upload boundary, sparse acknowledgment result shape, no-removal-possible behavior, and out-of-scope boundaries in under 2 minutes; no lookup, upload, channel update, banner upload, thumbnail upload, video operation, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, or multi-endpoint workflow is introduced  
**Constraints**: Preserve endpoint mutation semantics, expose quota cost 50 in metadata/description/examples, require OAuth-only access, require exactly one non-empty target `channelId`, reject `body` and `media`, reject `onBehalfOfContentOwner` unless a narrow shared contract expansion is approved during implementation, map success to an acknowledgment rather than refreshed channel branding state, keep no-current-watermark/already-removed outcomes distinct from success, avoid leaking API keys, OAuth tokens, authorization details, raw upstream diagnostics, stack traces, sensitive access context, raw media content, or secret-bearing details in results or errors, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`watermarks_unset`), extension of the existing watermarks Layer 2 resource-family module, narrow public exports and default registry integration, replacement of the representative placeholder catalog entry with a concrete contract if still present, focused contract/unit/integration coverage, and documentation artifacts for YT-255 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-155 wrapper dependency, YT-255 seed requirements, shared Layer 2 contracts, existing watermarks module placement, existing representative catalog placeholder, and mutation patterns into one endpoint-specific `watermarks_unset` plan with quota cost `50`, OAuth-only access, required `channelId`, no-upload behavior, rejected partner delegation in this slice, safe acknowledgment result shaping, and distinct validation/access/permission/quota/not-found/no-removal/policy/upstream-refusal behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `watermarks_unset` contract builder, descriptor builder, handler builder, argument validator, channel-context helper, auth-context helper, acknowledgment result mapper, upstream-error mapper, local default executor, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for non-object arguments, missing `channelId`, blank or non-string `channelId`, ambiguous multi-target `channelId`, unsupported top-level fields, rejected `body`, rejected `media`, rejected `onBehalfOfContentOwner`, missing OAuth, API-key-only access, insufficient permission, forbidden or policy failure, not-found channel failure, quota failure, endpoint unavailable, deprecated endpoint behavior, no-current-watermark or already-removed behavior, sparse or no-content success shaping, out-of-scope upload/lookup/update/banner/thumbnail/video/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment requests, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── watermarks_unset.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── watermarks.py                    # Existing Layer 1 unset wrapper dependency from YT-155
├── tools/
│   ├── dispatcher.py                    # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                  # Public exports for watermarks_unset symbols
│       ├── contracts.py                 # Existing shared contract primitives
│       ├── conventions.py               # Existing response/error boundary helpers
│       ├── examples.py                  # Replace representative placeholder with concrete watermarks_unset contract
│       ├── families.py                  # Existing watermarks family placement metadata
│       └── watermarks.py                # Existing Layer 2 family; add unset contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_youtube_watermarks_contract.py
├── integration/
│   ├── test_youtube_tool_registration.py
│   └── test_youtube_watermarks_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_watermarks.py
```

**Structure Decision**: Extend the existing `watermarks.py` Layer 2 resource-family module created for YT-254 because `watermarks_set` and `watermarks_unset` share the same upstream resource family and test surfaces. YT-155 provides the matching Layer 1 resource wrapper, and YT-255 should remain separate from thumbnails, channel banners, channel metadata, videos, search, captions, playlists, comments, analytics, recommendations, and higher-level workflows. This keeps the public tool cohesive with the upstream `watermarks` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local YT-255 seed requirements: public `watermarks_unset` tool, official quota cost `50`, and clear OAuth documentation.
- Confirm existing YT-155 Layer 1 wrapper availability and whether the public YT-255 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, mutation-result, and example conventions in the local codebase.
- Confirm that the concrete Layer 2 watermarks module already exists for `watermarks_set` and choose the smallest extension plus export/dispatcher wiring needed for `watermarks_unset`.
- Confirm how to replace or align the current representative `watermarks_unset` placeholder entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing mutation acknowledgment tools, especially `watermarks_set`, `videos_delete`, and the YT-155 Layer 1 acknowledgment behavior, to choose the smallest consistent validation and acknowledgment shape.

**Red**: Identify missing planning facts that would block task generation, including supported request shape, OAuth handling, watermarks family placement, registration surface, acknowledgment result shape, no-removal-possible handling, safe error categories, examples, sparse or no-content success rules, unsupported field rejection, partner-delegation boundary, no-upload boundary, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into watermark upload, watermark placement updates, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflows, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/data-model.md)
- [contracts/watermarks_unset.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/contracts/watermarks_unset.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, target channel request contract, watermark-removal acknowledgment result shape, OAuth and quota caveats, `channelId` validation, rejected `body` and `media` shapes, rejected partner delegation, unsupported modifier rejection, safe error categories, no-removal-possible behavior, and no upload/lookup/update/banner/thumbnail/video/analytics/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `watermarks_unset`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, required `channelId`, no-upload rules, sparse acknowledgment behavior, no-removal-possible separation, no partner-delegation expansion in this slice, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Remove a Channel Watermark Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `watermarks_unset` is absent or incomplete until implemented, requires `channelId`, rejects `body`, `media`, setting payloads, and unsupported modifiers, invokes the Layer 1 watermark-unset wrapper once with OAuth context, and maps sparse or no-content success to a watermark-removal acknowledgment with endpoint, quota cost 50, target channel context, access context, availability state, and mutation details.

**Green**: Extend the existing `watermarks.py` Layer 2 module with constants, schema, contract builder, descriptor builder, handler, validator, channel helper, auth-context helper, acknowledgment mapper, default local executor, public exports, and dispatcher registration needed for successful watermark removals.

**Refactor**: Align naming, docstrings, acknowledgment mapping, and error mapping with existing Layer 2 mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Quota, OAuth, and Removal Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `channelId`, no-upload boundary, sparse acknowledgment result shape, no-removal-possible caveat, rejected `onBehalfOfContentOwner`, safe result guidance, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful authorized watermark removal, sparse success, missing channel validation failure, malformed channel failure, unsupported metadata or upload failure, rejected partner delegation, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, no-removal-possible outcome, and out-of-scope workflow rejection.

**Refactor**: Replace the existing representative `watermarks_unset` placeholder contract with the concrete contract builder and remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required `channelId`, no-upload boundary, acknowledgment behavior, partner-delegation boundary, and unsupported-input guidance reviewable in `watermarks.py`.

### User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Removal Requests Clearly

**Red**: Add failing validation and error-mapping checks for non-object arguments, missing `channelId`, blank or non-string `channelId`, ambiguous multi-target `channelId`, unsupported top-level fields, supplied `body`, supplied `media`, supplied `onBehalfOfContentOwner`, upload fields, metadata fields, lookup fields, update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, forbidden or policy failure, not-found failure, no-current-watermark or already-removed behavior, deprecated behavior, sparse success, upstream refusal, conflict behavior where observable, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, target context extraction, acknowledgment context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, raw media content, unsafe request context, authorization headers, sensitive authorization details, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the official endpoint request shape exposed by the Layer 1 wrapper.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_watermarks_contract.py`, `tests/integration/test_youtube_watermarks_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Create and export `WATERMARKS_UNSET_*` symbols, import and use `build_watermarks_unset_wrapper()`, add `build_watermarks_unset_tool_descriptor()` to the default registry, and align representative contract/example coverage while preserving the public tool name `watermarks_unset`.

**Refactor**: Keep `watermarks.py` cohesive, keep Layer 1 changes narrow, and avoid changes to thumbnails, channel banners, channels, videos, search, captions, playlists, comments, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Branding mutation risk**: Watermark removal changes channel branding. Validation must require explicit target channel context before execution, and examples must use test-safe identifiers.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Access risk**: Watermark removal is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, or credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **No-upload boundary risk**: Callers may confuse unset with set. Validation and documentation must reject and explain `body`, `media`, watermark metadata, upload content, and upload-only request shapes.
- **Sparse result risk**: Successful `watermarks.unset` can return sparse or no refreshed branding state. Result mapping must provide a useful acknowledgment without fabricating channel metadata, watermark lookup state, media hosting URLs, analytics, recommendations, rankings, summaries, or enrichment.
- **No-removal risk**: A valid request can encounter no-current-watermark, already-removed, not-found, ownership, permissions, policy, quota, service constraint, or channel availability outcomes. These must remain distinct from local validation failures and successful acknowledgments.
- **Scope risk**: Do not add watermark upload, watermark placement updates, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, raw uploaded media, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `watermarks_unset` should live beside `watermarks_set` in the existing watermarks Layer 2 module, not in thumbnails, channel banners, channels, videos, search, captions, playlists, comments, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_watermarks_contract.py tests/unit/test_youtube_watermarks.py tests/integration/test_youtube_watermarks_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
