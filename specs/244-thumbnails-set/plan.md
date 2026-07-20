# Implementation Plan: Layer 2 Thumbnails Set Tool

**Branch**: `244-thumbnails-set` | **Date**: 2026-07-20 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `thumbnails_set` for the YouTube endpoint operation `thumbnails.set`. The implementation will add the thumbnails Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`, reuse the existing Layer 1 `build_thumbnails_set_wrapper()` from YT-144, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth disclosure, media-upload request validation, near-raw mutation result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and narrow: it requires a non-empty video `videoId`, requires a supported `media` upload payload, costs 50 official quota units per call, requires OAuth-backed authorization, returns a thumbnail-set result with safe target and upload context, and does not add thumbnail generation, image editing or transformation, video upload, video metadata updates, channel branding, analytics, ranking, summarization, enrichment, preflight lookup, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 family registry at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`; existing Layer 1 `thumbnails.set` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/thumbnails.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, upload descriptors, thumbnail-set results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including thumbnails set contract builders, descriptor builders, handler builders, argument validators, video-id helpers, media-upload helpers, OAuth-context helpers, thumbnail-set result mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single thumbnail-set request performs one Layer 1 wrapper call and local validation proportional only to supplied fields; no video lookup, thumbnail generation, image transformation, video metadata update, analytics, ranking, summarization, enrichment, bulk processing, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint media-upload semantics, expose quota cost 50 in metadata/description/examples, declare OAuth-required access, require a non-empty `videoId`, require supported `media` upload content, reject unsupported fields and out-of-scope modifiers before execution, avoid leaking credential material, raw upload bytes, or raw diagnostics in results or errors, add code under the thumbnails Layer 2 resource-family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`thumbnails_set`), one new thumbnails Layer 2 resource-family module, narrow public exports and default registry integration, replacement or superseding of any representative catalog placeholder if present, focused contract/unit/integration coverage, and documentation artifacts for YT-244 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-144 wrapper, YT-244 seed, shared Layer 2 contracts, and existing media-upload mutation tools agree on quota cost `50`, OAuth-required access, required `videoId`, required `media` upload content, safe upload descriptors, sparse result handling, unsupported modifier rejection, and distinct validation/access/target-video/upload/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `thumbnails_set` contract builder, descriptor builder, handler builder, argument validator, video-id helper, media helper, OAuth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, catalog/example helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `videoId`, empty `videoId`, non-string `videoId`, missing `media`, empty media content, unsupported media shape, unsupported MIME type when locally classified, unsupported request fields, video metadata update attempts, image transformation attempts, thumbnail generation attempts, listing selectors, missing OAuth, target-video not found or ineligible, upstream upload rejection, quota failures, upstream invalid requests, authorization failures, endpoint unavailable, deprecated endpoint behavior, sparse result shaping, safe upload context, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── thumbnails_set.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── thumbnails.py        # Existing Layer 1 set wrapper dependency from YT-144
├── tools/
│   ├── dispatcher.py        # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py      # Public exports for thumbnails_set symbols
│       ├── contracts.py     # Existing shared contract primitives
│       ├── examples.py      # Representative shared contract set, if catalog export requires update
│       ├── families.py      # Existing thumbnails family placement metadata
│       └── thumbnails.py    # New Layer 2 thumbnails family; add set contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_thumbnails_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_thumbnails_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_thumbnails.py
```

**Structure Decision**: Add the concrete `thumbnails.py` Layer 2 resource-family module because `families.py` already reserves the thumbnails family, YT-144 provides the matching Layer 1 resource module, and this slice should remain separate from playlist image media uploads, video metadata updates, channel branding, and higher-level workflow modules. This keeps the public tool cohesive with the upstream `thumbnails` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `thumbnails.set` quota, OAuth mode, required `videoId`, required `media`, supported media boundary, response shape, sparse success behavior, and documented error categories.
- Confirm existing YT-144 Layer 1 wrapper availability and whether the public YT-244 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, mutation response, media-upload, error, availability, and example conventions in the local codebase.
- Confirm current thumbnails Layer 2 family placement and whether a new `youtube_common/thumbnails.py` module should be created rather than reusing playlist-image, video, or channel modules.
- Confirm how to add or replace any representative `thumbnails_set` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing media-upload and mutation tools, especially `playlistImages_insert`, `playlistImages_update`, `channelBanners_insert`, `captions_insert`, and `captions_update`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported target input shape, media shape, OAuth handling, thumbnails family placement, registration surface, thumbnail-set result shape, safe error categories, examples, target-video caveats, sparse response behavior, upload sanitization rules, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into thumbnail generation, image editing, video upload, video metadata updates, channel branding, analytics, ranking, summarization, enrichment, preflight lookup, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/data-model.md)
- [contracts/thumbnails_set.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/contracts/thumbnails_set.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, media-upload request contract, thumbnail-set result shape, OAuth and quota caveats, `videoId` validation, `media` validation, unsupported modifier rejection, safe upload descriptors, sparse response handling, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `thumbnails_set`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required access disclosure, quota accuracy, media-upload boundaries, target-video validation, sparse-response behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Set a Video Thumbnail Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `thumbnails_set` is absent until implemented, requires a non-empty `videoId`, requires supported `media`, requires OAuth-backed access, invokes the Layer 1 set wrapper once, and maps success to a thumbnail-set result with endpoint, quota cost 50, target video context, upload context, OAuth context, and any safe returned thumbnail fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, video-id helper, media helper, result mapper, default local set transport, default executor, public exports, and dispatcher registration needed for successful thumbnail setting.

**Refactor**: Align naming, docstrings, helper reuse, upload caveats, OAuth handling, target-video context, and error mapping with media-upload mutation tools and shared mutation-result conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Upload Requirements Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth requirement, required `videoId`, required `media`, upload boundary, thumbnail-set result shape, sparse response caveat, target-video caveats, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful thumbnail setting, sparse success handling, missing `videoId`, missing `media`, invalid `videoId`, unsupported upload content, missing authorization, target-video or quota upstream failure, and out-of-scope thumbnail-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required video id, upload requirement, target-video caveats, sparse response caveat, and unsupported-input guidance reviewable in `thumbnails.py`.

### User Story 3 - Reject Invalid or Under-Authorized Thumbnail Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `videoId`, empty `videoId`, non-string `videoId`, missing `media`, malformed `media`, missing media content, unsupported media MIME type when classified locally, unsafe raw media echo, unsupported top-level fields, metadata-update attempts, image-transformation attempts, thumbnail-generation prompts, listing selectors, missing OAuth, insufficient OAuth, target video missing, target video not writable or thumbnail-ineligible, quota failure, endpoint unavailable, upstream invalid request, deprecated behavior, and unexpected upstream failure.

**Green**: Implement validator, OAuth-context selection, upload-context extraction, thumbnail-set context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upload bytes, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_thumbnails_contract.py`, `tests/integration/test_youtube_thumbnails_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `THUMBNAILS_SET_*` symbols, add `build_thumbnails_set_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `thumbnails.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist images, videos, channel branding, media transfer infrastructure, analytics, recommendations, search, or higher-level workflow modules.

## Risk and Mitigation

- **Upload-boundary risk**: The tool must require thumbnail upload content and must never echo raw upload bytes. Tests and examples must prove target-only, upload-only, missing-media, malformed-media, and unsupported-media requests fail before execution.
- **OAuth risk**: Thumbnail setting requires eligible OAuth-backed authorization. The handler must reject missing or insufficient OAuth before execution and must not expose tokens in results, errors, logs, or examples.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Target-video risk**: A valid `videoId` can still target a video that is unavailable, unwritable, or ineligible for custom thumbnails. Safe error mapping must keep these outcomes distinct from local validation and missing OAuth.
- **Sparse-result risk**: Successful upstream responses may omit full thumbnail or video resource details. Result mapping must preserve target and operation context without fabricating missing fields.
- **Scope risk**: Do not add thumbnail generation, image editing, video upload, video metadata updates, channel branding, analytics, recommendation, ranking, summarization, enrichment, preflight lookup, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upload bytes, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, target-owner details, or secret-bearing details in failures, logs, metadata, or examples.
- **Cohesion risk**: `thumbnails_set` should live in the new `thumbnails` Layer 2 module, not in playlist images, videos, channels, media infrastructure, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_thumbnails_contract.py tests/unit/test_youtube_thumbnails.py tests/integration/test_youtube_thumbnails_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
