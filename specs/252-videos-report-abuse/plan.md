# Implementation Plan: Layer 2 Tool `videos_reportAbuse`

**Branch**: `252-videos-report-abuse` | **Date**: 2026-07-23 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videos_reportAbuse` for the YouTube endpoint operation `videos.reportAbuse`. The implementation will extend the existing videos Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, reuse the existing Layer 1 `build_videos_report_abuse_wrapper()` from YT-152, and follow YT-201/YT-202 shared contract conventions for naming, 50-unit quota disclosure, OAuth-only access disclosure, bounded abuse-report body validation, no-content mutation acknowledgment result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and mutation-oriented: it requires a `body` object with `videoId` and `reasonId`, supports only `secondaryReasonId`, `comments`, and `language` as optional body fields in this slice, requires OAuth for every request, rejects partner-only `onBehalfOfContentOwner`, request-shape aliases, unsupported modifiers, and out-of-scope workflow fields before execution, acknowledges successful no-content report submissions, and does not add abuse-reason discovery, automated abuse classification, evidence gathering, moderation decisions, video metadata lookup, rating, deletion, comment moderation, captions, transcripts, analytics, recommendations, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing videos Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`; existing Layer 1 `videos.reportAbuse` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`; existing Layer 1 videos validators under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, abuse-report acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including videos report-abuse contract builders, descriptor builders, handler builders, argument validators, abuse-report body helpers, OAuth-context helpers, acknowledgment result mappers, upstream-error mappers, local default executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single abuse-report invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 50-unit quota cost, OAuth requirement, required `body.videoId`, required `body.reasonId`, supported optional body fields, no-content acknowledgment result shape, and out-of-scope boundaries in under 2 minutes; no abuse-reason lookup, policy classification, evidence collection, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, media transfer, or multi-endpoint workflow is introduced  
**Constraints**: Preserve endpoint report-submission semantics, expose quota cost 50 in metadata/description/examples, require OAuth-only access, require `body.videoId` plus `body.reasonId`, support only `body.secondaryReasonId`, `body.comments`, and `body.language` as optional body fields, reject `onBehalfOfContentOwner` and unsupported fields unless a narrow Layer 1 contract expansion is approved during implementation, map success to an acknowledgment rather than a refreshed video resource or moderation decision, avoid leaking API keys, OAuth tokens, authorization details, raw upstream diagnostics, stack traces, sensitive report details beyond caller-provided safe context, or unsafe request context in results or errors, keep changes under the videos Layer 2 family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videos_reportAbuse`), endpoint-specific additions to the existing videos Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-252 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-152 wrapper dependency, YT-252 seed requirements, official endpoint behavior, shared Layer 2 contracts, and existing videos module pattern into one endpoint-specific `videos_reportAbuse` plan with quota cost `50`, OAuth-only access, required `body.videoId` and `body.reasonId`, optional `body.secondaryReasonId`, `body.comments`, and `body.language`, no partner delegation in this slice, safe no-content acknowledgment result shaping, and distinct validation/access/quota/not-found/policy/upstream-refusal behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videos_reportAbuse` contract builder, descriptor builder, handler builder, argument validator, abuse-report body helper, auth-context helper, acknowledgment result mapper, upstream-error mapper, local default executor, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `body`, non-object `body`, missing `body.videoId`, empty or non-string `body.videoId`, missing `body.reasonId`, empty or non-string `body.reasonId`, unsupported or unavailable reason values, malformed optional body fields, unsupported body fields, unsupported top-level fields, rejected `onBehalfOfContentOwner`, missing OAuth, API-key-only access, invalid reason upstream failures, duplicate-report-style upstream refusals where observable, forbidden or policy failure, not-found failure, quota failure, endpoint unavailable, deprecated endpoint behavior, no-content success shaping, out-of-scope abuse-reason discovery/classification/evidence/moderation/lookup/rating/delete/comment/caption/transcript/analytics/recommendation/ranking/summarization/enrichment requests, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos_reportAbuse.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   ├── videos.py                       # Existing Layer 1 reportAbuse wrapper dependency from YT-152
│   └── validators/videos.py            # Existing Layer 1 videos.reportAbuse body validation dependency
├── tools/
│   ├── dispatcher.py                   # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                 # Public exports for videos_reportAbuse symbols
│       ├── contracts.py                # Existing shared contract primitives
│       ├── conventions.py              # Existing response/error boundary helpers
│       ├── examples.py                 # Representative shared contract set; add concrete videos_reportAbuse contract if needed
│       ├── families.py                 # Existing videos family placement metadata
│       └── videos.py                   # Existing Layer 2 family; add reportAbuse contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `videos.py` Layer 2 resource-family module because YT-247 through YT-251 established videos family placement, YT-152 provides the matching Layer 1 resource wrapper, and YT-252 should remain separate from abuse-reason lookup, rating lookup/mutation, deletion, search, captions, thumbnails, playlists, comments, analytics, recommendations, and higher-level workflows. This keeps the public tool cohesive with the upstream `videos` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current official `videos.reportAbuse` quota, OAuth mode, required request body fields, optional body fields, optional partner delegation caveat, no-content success response, and documented error categories.
- Confirm existing YT-152 Layer 1 wrapper availability and whether the public YT-252 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, mutation-result, and example conventions in the local codebase.
- Confirm current videos Layer 2 family placement and how to add `videos_reportAbuse` beside `videos_list`, `videos_insert`, `videos_update`, `videos_rate`, and `videos_getRating` in the existing `youtube_common/videos.py` module.
- Confirm how to add any representative `videos_reportAbuse` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing mutation tools, especially `videos_rate`, `comments_setModerationStatus`, `comments_delete`, `playlistImages_delete`, `subscriptions_delete`, and the YT-152 Layer 1 acknowledgment behavior, to choose the smallest consistent acknowledgment shape.

**Red**: Identify missing planning facts that would block task generation, including supported body shape, OAuth handling, videos family placement, registration surface, acknowledgment result shape, safe error categories, examples, no-content rules, unsupported field rejection, partner-delegation boundary, official endpoint caveats, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into abuse-reason discovery, automated classification, evidence collection, moderation decisions, video metadata lookup, rating lookup/mutation, deletion, comment moderation, caption management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/data-model.md)
- [contracts/videos_reportAbuse.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/contracts/videos_reportAbuse.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/252-videos-report-abuse/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, abuse-report request contract, acknowledgment result shape, OAuth and quota caveats, `body.videoId` validation, `body.reasonId` validation, optional body-field validation, rejected partner delegation, unsupported modifier rejection, safe error categories, and no classification/moderation/lookup/rating/delete/analytics/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videos_reportAbuse`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, abuse-report body boundaries, no-content acknowledgment behavior, no partner-delegation expansion in this slice, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Submit an Abuse Report Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `videos_reportAbuse` is absent until implemented, requires `body.videoId`, requires `body.reasonId`, accepts only supported optional body fields, invokes the Layer 1 report-abuse wrapper once with OAuth context, and maps no-content success to an abuse-report acknowledgment with endpoint, quota cost 50, target video identity, submitted reason, access context, availability state, and mutation details.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, abuse-report body helper, auth-context helper, acknowledgment mapper, default local no-content executor, public exports, and dispatcher registration needed for successful abuse-report submission.

**Refactor**: Align naming, docstrings, helper reuse, acknowledgment mapping, and error mapping with existing Layer 2 mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Quota, OAuth, and Payload Expectations Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `body.videoId`, required `body.reasonId`, supported `body.secondaryReasonId`, `body.comments`, and `body.language`, no-content acknowledgment result shape, rejected `onBehalfOfContentOwner`, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful authorized report submission, missing body failure, missing target failure, missing reason failure, unsupported optional field failure, rejected partner delegation, missing OAuth failure, quota or upstream failure, unavailable target failure, upstream refusal, and out-of-scope workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required body fields, optional body-field rules, no-content acknowledgment behavior, partner-delegation boundary, and unsupported-input guidance reviewable in `videos.py`.

### User Story 3 - Reject Invalid or Unsupported Abuse-Report Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `body`, non-object `body`, missing `videoId`, blank or non-string `videoId`, missing `reasonId`, blank or non-string `reasonId`, unsupported reason values where locally detectable, malformed `secondaryReasonId`, malformed `comments`, malformed `language`, unsupported body fields, unsupported top-level fields, supplied `onBehalfOfContentOwner`, abuse-reason lookup fields, automated classification fields, evidence fields, moderation fields, metadata lookup fields, rating fields, delete fields, comment/caption/transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, forbidden or policy failure, not-found failure, deprecated behavior, no-content success, upstream refusal, duplicate-report-style behavior where observable, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, abuse-report context extraction, acknowledgment context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, authorization headers, sensitive report details beyond safe caller context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the official endpoint request body shape.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_videos_contract.py`, `tests/integration/test_youtube_videos_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEOS_REPORT_ABUSE_*` symbols, import and use `build_videos_report_abuse_wrapper()`, add `build_videos_report_abuse_tool_descriptor()` to the default registry, and add representative contract/example coverage while preserving the public tool name `videos_reportAbuse`.

**Refactor**: Keep `videos.py` cohesive, keep Layer 1 changes narrow, and avoid changes to search, captions, video abuse report reasons, video categories, thumbnails, playlists, comments, rating lookup/mutation, deletion, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Sensitive mutation risk**: Abuse reporting submits a user-affecting policy report. Validation must require explicit target video and reason before execution, and examples must use test-safe identifiers.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Access risk**: Video abuse reporting is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, or credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **Payload-boundary risk**: The public tool accepts only `body.videoId`, `body.reasonId`, `body.secondaryReasonId`, `body.comments`, and `body.language` in this slice. Unsupported fields and partner-only `onBehalfOfContentOwner` must be rejected or left unexposed until the Layer 1 contract is deliberately expanded.
- **No-content result risk**: Successful `videos.reportAbuse` returns no refreshed video resource. Result mapping must provide a useful acknowledgment without fabricating moderation decisions, abuse classification, video metadata, evidence, analytics, recommendations, rankings, summaries, or enrichment.
- **Policy-refusal risk**: A valid request can still be refused due to target availability, caller eligibility, duplicate-report behavior, invalid reason, or policy constraints. These outcomes must remain distinct from local validation failures and successful acknowledgments.
- **Scope risk**: Do not add abuse-reason discovery, automated abuse classification, evidence collection, moderation decisions, video metadata lookup, rating lookup/mutation, deletion, comment moderation, caption management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `videos_reportAbuse` should live in the existing videos Layer 2 module, not in video abuse reason lookup, search, captions, thumbnails, playlists, comments, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
