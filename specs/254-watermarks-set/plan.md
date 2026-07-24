# Implementation Plan: Layer 2 Tool `watermarks_set`

**Branch**: `254-watermarks-set` | **Date**: 2026-07-24 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `watermarks_set` for the YouTube endpoint operation `watermarks.set`. The implementation will add a focused Layer 2 watermarks resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`, reuse the existing Layer 1 `build_watermarks_set_wrapper()` from YT-154, and follow YT-201/YT-202 shared contract conventions for naming, 50-unit quota disclosure, OAuth-only access disclosure, media-upload guidance, watermark metadata validation, safe mutation or upload acknowledgment result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and mutation-oriented: it requires exactly one target `channelId`, one watermark `body` metadata payload with timing and position details, and one `media` upload payload; requires OAuth for every request; rejects metadata-only, media-only, unsupported media, unsupported fields, partner delegation, bulk watermark shapes, aliases, and out-of-scope workflow fields before execution; acknowledges successful sparse or no-content watermark-set operations; and does not add watermark removal, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflow, or higher-level research behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; new watermarks Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`; existing Layer 1 `watermarks.set` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, upload descriptors, watermark-update acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including watermarks set contract builders, descriptor builders, handler builders, argument validators, channel-context helpers, body metadata validators, media upload validators, upload-context helpers, OAuth-context helpers, acknowledgment result mappers, upstream-error mappers, local default executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single watermark-set invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 50-unit quota cost, OAuth requirement, required `channelId`, required watermark `body`, required `media`, supported upload boundary, sparse acknowledgment result shape, and out-of-scope boundaries in under 2 minutes; no lookup, removal, channel update, banner upload, thumbnail upload, video operation, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, or multi-endpoint workflow is introduced  
**Constraints**: Preserve endpoint upload mutation semantics, expose quota cost 50 in metadata/description/examples, require OAuth-only access, require exactly one non-empty target `channelId`, require `body.timing` and `body.position`, allow optional `body.targetChannelId` only when it is text, require `media.mimeType` plus `media.content`, keep supported watermark MIME types aligned with the Layer 1 boundary (`image/jpeg`, `image/png`, and `application/octet-stream`), keep the 10 MB upload boundary visible, reject metadata-only and media-only request shapes, reject `onBehalfOfContentOwner` unless a narrow shared contract expansion is approved during implementation, map success to an acknowledgment rather than refreshed channel branding state, avoid leaking API keys, OAuth tokens, authorization details, raw media content, raw upstream diagnostics, stack traces, sensitive access context, or secret-bearing details in results or errors, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`watermarks_set`), creation of the watermarks Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent or only representative, focused contract/unit/integration coverage, and documentation artifacts for YT-254 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-154 wrapper dependency, YT-254 seed requirements, shared Layer 2 contracts, and existing upload/mutation patterns into one endpoint-specific `watermarks_set` plan with quota cost `50`, OAuth-only access, required `channelId`, required `body`, required `media`, 10 MB upload guidance, accepted media types, no partner delegation in this slice, safe acknowledgment result shaping, and distinct validation/access/permission/quota/not-found/policy/upload/upstream-refusal behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `watermarks_set` contract builder, descriptor builder, handler builder, argument validator, channel-context helper, body metadata validator, media upload validator, upload-context helper, auth-context helper, acknowledgment result mapper, upstream-error mapper, local default executor, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `channelId`, blank or non-string `channelId`, missing `body`, incomplete `body.timing`, incomplete `body.position`, invalid `body.targetChannelId`, missing `media`, invalid `media.mimeType`, empty or oversized `media.content`, unsupported top-level fields, rejected `onBehalfOfContentOwner`, metadata-only requests, media-only requests, missing OAuth, API-key-only access, insufficient permission, forbidden or policy failure, not-found channel failure, quota failure, endpoint unavailable, deprecated endpoint behavior, sparse or no-content success shaping, out-of-scope removal/lookup/update/banner/thumbnail/video/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment requests, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── watermarks_set.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── watermarks.py                    # Existing Layer 1 set wrapper dependency from YT-154
├── tools/
│   ├── dispatcher.py                    # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                  # Public exports for watermarks_set symbols
│       ├── contracts.py                 # Existing shared contract primitives
│       ├── conventions.py               # Existing response/error boundary helpers
│       ├── examples.py                  # Representative shared contract set; align concrete watermarks_set contract
│       ├── families.py                  # Existing watermarks family placement metadata
│       └── watermarks.py                # New Layer 2 family; add set contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Add a new `watermarks.py` Layer 2 resource-family module because the watermarks family is already listed in shared family metadata but has no concrete Layer 2 module yet. YT-154 provides the matching Layer 1 resource wrapper, and YT-254 should remain separate from thumbnails, channel banners, channel metadata, videos, search, captions, playlists, comments, analytics, recommendations, and higher-level workflows. This keeps the public tool cohesive with the upstream `watermarks` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local YT-254 seed requirements: public `watermarks_set` tool, official quota cost `50`, and clear media-upload plus OAuth documentation.
- Confirm existing YT-154 Layer 1 wrapper availability and whether the public YT-254 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, upload-result, mutation-result, and example conventions in the local codebase.
- Confirm that no concrete Layer 2 watermarks module exists yet and choose the smallest new module plus export/dispatcher wiring needed for `watermarks_set`.
- Confirm how to align or replace any representative `watermarks_set` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing upload mutation tools, especially `thumbnails_set`, `playlistImages_insert`, `playlistImages_update`, and the YT-154 Layer 1 acknowledgment behavior, to choose the smallest consistent validation and acknowledgment shape.

**Red**: Identify missing planning facts that would block task generation, including supported request shape, OAuth handling, watermarks family placement, registration surface, acknowledgment result shape, safe error categories, examples, sparse or no-content success rules, unsupported field rejection, partner-delegation boundary, upload boundary, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into watermark removal, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflows, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/data-model.md)
- [contracts/watermarks_set.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/contracts/watermarks_set.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, target channel request contract, body metadata contract, media upload contract, watermark-update acknowledgment result shape, OAuth and quota caveats, `channelId` validation, rejected metadata-only and media-only shapes, rejected partner delegation, unsupported modifier rejection, media safety, safe error categories, and no removal/lookup/update/banner/thumbnail/video/analytics/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `watermarks_set`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, required `channelId`, required `body`, required `media`, upload-boundary rules, sparse acknowledgment behavior, no partner-delegation expansion in this slice, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Set a Channel Watermark Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `watermarks_set` is absent until implemented, requires `channelId`, `body`, and `media`, rejects metadata-only/media-only shapes and unsupported modifiers, invokes the Layer 1 watermark-set wrapper once with OAuth context, and maps sparse or no-content success to a watermark-update acknowledgment with endpoint, quota cost 50, target channel identity, watermark metadata context, media upload context, access context, availability state, and mutation details.

**Green**: Add the smallest new `watermarks.py` Layer 2 module with constants, schema, contract builder, descriptor builder, handler, validator, channel helper, body metadata helper, media upload helper, auth-context helper, acknowledgment mapper, default local executor, public exports, and dispatcher registration needed for successful watermark updates.

**Refactor**: Align naming, docstrings, helper reuse, upload sanitization, acknowledgment mapping, and error mapping with existing Layer 2 mutation/upload tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Quota, OAuth, and Upload Requirements Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `channelId`, required `body`, required `media`, accepted media types, 10 MB upload limit, sparse acknowledgment result shape, rejected `onBehalfOfContentOwner`, media safety guidance, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful authorized watermark update, sparse success, missing channel validation failure, malformed channel failure, missing metadata failure, unsupported metadata failure, missing upload failure, unsupported upload failure, rejected partner delegation, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, and out-of-scope workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required `channelId`, required `body`, required `media`, upload boundary, acknowledgment behavior, partner-delegation boundary, and unsupported-input guidance reviewable in `watermarks.py`.

### User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Watermark Requests Clearly

**Red**: Add failing validation and error-mapping checks for non-object arguments, missing `channelId`, blank or non-string `channelId`, missing `body`, non-object `body`, missing or empty `body.timing`, missing or empty `body.position`, non-string `body.targetChannelId`, unsupported body fields if the contract narrows them, missing `media`, non-object `media`, unsupported `media.mimeType`, missing or empty `media.content`, oversized media where locally detectable, unsupported top-level fields, supplied `onBehalfOfContentOwner`, metadata-only requests, media-only requests, removal fields, lookup fields, update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, forbidden or policy failure, not-found failure, deprecated behavior, sparse success, upstream refusal, conflict behavior where observable, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, target context extraction, body metadata context extraction, upload descriptor extraction, acknowledgment context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, raw media content, unsafe request context, authorization headers, sensitive authorization details, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the official endpoint request shape exposed by the Layer 1 wrapper.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_watermarks_contract.py`, `tests/integration/test_youtube_watermarks_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Create and export `WATERMARKS_SET_*` symbols, import and use `build_watermarks_set_wrapper()`, add `build_watermarks_set_tool_descriptor()` to the default registry, and align representative contract/example coverage while preserving the public tool name `watermarks_set`.

**Refactor**: Keep `watermarks.py` cohesive, keep Layer 1 changes narrow, and avoid changes to thumbnails, channel banners, channels, videos, search, captions, playlists, comments, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Branding mutation risk**: Watermark setting changes channel branding. Validation must require explicit target channel identity, watermark metadata, and upload content before execution, and examples must use test-safe identifiers.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Access risk**: Watermark setting is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, raw media content, or credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **Upload risk**: Media content may be private or large. Validation and result mapping must preserve only safe descriptors such as MIME type and content-present status, never raw image content.
- **Metadata boundary risk**: Watermark `body` must include timing and position metadata. Missing, unsupported, or incompatible metadata must be rejected before execution when locally detectable.
- **Sparse result risk**: Successful `watermarks.set` can return sparse or no refreshed branding state. Result mapping must provide a useful acknowledgment without fabricating channel metadata, watermark lookup state, hosting URLs, analytics, recommendations, rankings, summaries, or enrichment.
- **Policy-refusal risk**: A valid request can still be refused due to ownership, permissions, policy state, branding eligibility, upload eligibility, quota state, service constraints, or channel availability. These outcomes must remain distinct from local validation failures and successful acknowledgments.
- **Scope risk**: Do not add watermark removal, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, raw uploaded media, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `watermarks_set` should live in the new watermarks Layer 2 module, not in thumbnails, channel banners, channels, videos, search, captions, playlists, comments, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_watermarks_contract.py tests/unit/test_youtube_watermarks.py tests/integration/test_youtube_watermarks_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
