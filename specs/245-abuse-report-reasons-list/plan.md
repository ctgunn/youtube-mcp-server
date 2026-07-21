# Implementation Plan: Layer 2 Tool `videoAbuseReportReasons_list`

**Branch**: `245-abuse-report-reasons-list` | **Date**: 2026-07-20 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videoAbuseReportReasons_list` for the YouTube endpoint operation `videoAbuseReportReasons.list`. The implementation will add a concrete Layer 2 video-abuse-report-reasons resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`, reuse the existing Layer 1 `build_video_abuse_report_reasons_list_wrapper()` from YT-145, and follow YT-201/YT-202 shared contract conventions for naming, quota, API-key access disclosure, localization-aware request validation, near-raw list result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and read-only: it requires `part` and `hl`, costs 1 official quota unit per call, uses API-key access expectations, returns a localized abuse-report-reason catalog when available, preserves empty successful results distinctly, and does not add video abuse report submission, report status lookup, moderation action, policy adjudication, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 family registry at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`; existing Layer 1 `videoAbuseReportReasons.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_abuse_report_reasons.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, localized reason results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including video abuse report reasons contract builders, descriptor builders, handler builders, argument validators, part-selection helpers, localization helpers, result mappers, empty-result helpers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single abuse-reason lookup performs one Layer 1 wrapper call and local validation proportional only to supplied fields; no report submission, policy evaluation, moderation workflow, video lookup, ranking, summarization, enrichment, bulk processing, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint lookup semantics, expose quota cost 1 in metadata/description/examples, declare API-key access expectation, require non-empty `part` and `hl`, reject unsupported fields and out-of-scope modifiers before execution, preserve empty item collections as successful lookups, avoid leaking API keys, authorization details, raw upstream diagnostics, stack traces, or unsafe request context in results or errors, add code under the video-abuse-report-reasons Layer 2 resource-family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videoAbuseReportReasons_list`), one new video-abuse-report-reasons Layer 2 resource-family module, narrow public exports and default registry integration, replacement or superseding of any representative catalog placeholder if present, focused contract/unit/integration coverage, and documentation artifacts for YT-245 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-145 wrapper, YT-245 seed, shared Layer 2 contracts, and existing read/list tools agree on quota cost `1`, API-key access, required `part`, required `hl`, localized lookup behavior, empty successful result handling, unsupported modifier rejection, and distinct validation/access/quota/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videoAbuseReportReasons_list` contract builder, descriptor builder, handler builder, argument validator, part-selection helper, localization helper, result mapper, empty-result helper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, catalog/example helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, empty `part`, non-string `part`, missing `hl`, empty `hl`, malformed `hl`, unsupported optional fields, paging controls, lookup selectors, video identifiers, report-submission payloads, moderation instructions, policy-evaluation instructions, ranking/summarization/enrichment fields, missing API-key access, upstream empty item collections, quota failures, upstream invalid requests, authorization failures, endpoint unavailable, deprecated endpoint behavior, sparse result shaping, localization context preservation, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videoAbuseReportReasons_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── video_abuse_report_reasons.py    # Existing Layer 1 list wrapper dependency from YT-145
├── tools/
│   ├── dispatcher.py                    # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                  # Public exports for videoAbuseReportReasons_list symbols
│       ├── contracts.py                 # Existing shared contract primitives
│       ├── examples.py                  # Representative shared contract set, if catalog export requires update
│       ├── families.py                  # Existing video_abuse_report_reasons family placement metadata
│       └── video_abuse_report_reasons.py # New Layer 2 family; add list contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_video_abuse_report_reasons_contract.py
│   ├── test_youtube_common_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_video_abuse_report_reasons_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_video_abuse_report_reasons.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Add the concrete `video_abuse_report_reasons.py` Layer 2 resource-family module because `families.py` already reserves the `video_abuse_report_reasons` family, YT-145 provides the matching Layer 1 resource module, and this slice should remain separate from `videos_reportAbuse`, moderation, policy interpretation, search, and higher-level reporting workflows. This keeps the public tool cohesive with the upstream `videoAbuseReportReasons` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `videoAbuseReportReasons.list` quota, API-key auth mode, required `part`, required `hl`, localized lookup behavior, response shape, empty-result behavior, and documented error categories.
- Confirm existing YT-145 Layer 1 wrapper availability and whether the public YT-245 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, localization, and example conventions in the local codebase.
- Confirm current video-abuse-report-reasons Layer 2 family placement and whether a new `youtube_common/video_abuse_report_reasons.py` module should be created rather than reusing videos, comments, moderation, or localization modules.
- Confirm how to add or replace any representative `videoAbuseReportReasons_list` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing read/list tools, especially `guideCategories_list`, `i18nLanguages_list`, `i18nRegions_list`, `search_list`, and `membershipsLevels_list`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, localization shape, API-key handling, video-abuse-report-reasons family placement, registration surface, reason-list result shape, safe error categories, examples, empty-result behavior, unsupported modifier rejection, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into video abuse report submission, moderation action, policy adjudication, report status lookup, ranking, summarization, enrichment, analytics, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/data-model.md)
- [contracts/videoAbuseReportReasons_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/contracts/videoAbuseReportReasons_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, localization request contract, reason-list result shape, API-key and quota caveats, `part` validation, `hl` validation, unsupported modifier rejection, empty successful result handling, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videoAbuseReportReasons_list`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, API-key access disclosure, quota accuracy, required localization boundary, empty-response behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Abuse Report Reasons Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `videoAbuseReportReasons_list` is absent until implemented, requires non-empty `part`, requires non-empty `hl`, invokes the Layer 1 list wrapper once with API-key auth, and maps success to a reason-list result with endpoint, quota cost 1, requested parts, localization context, access context, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, part helper, localization helper, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful localized reason lookup.

**Refactor**: Align naming, docstrings, helper reuse, localization handling, empty-result handling, and error mapping with existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Access, and Localization Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, API-key access disclosure, required `part`, required `hl`, localized result shape, empty-result caveat, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for localized reason lookup, populated success, empty success, missing part, missing display-language input, invalid part, invalid localization, missing access, quota or upstream failure, and out-of-scope report-submission request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, API-key access, required part, required `hl`, localization behavior, empty-result caveat, and unsupported-input guidance reviewable in `video_abuse_report_reasons.py`.

### User Story 3 - Reject Invalid or Unsupported Lookup Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, empty `part`, non-string `part`, missing `hl`, empty `hl`, malformed `hl`, unsupported top-level fields, paging controls, lookup selectors, video identifiers, report payloads, moderation instructions, policy evaluation instructions, ranking fields, summarization fields, enrichment fields, missing API-key access, quota failure, endpoint unavailable, upstream invalid request, deprecated behavior, empty upstream success, and unexpected upstream failure.

**Green**: Implement validator, API-key auth context selection, localization context extraction, reason-list context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_video_abuse_report_reasons_contract.py`, `tests/integration/test_youtube_video_abuse_report_reasons_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEO_ABUSE_REPORT_REASONS_LIST_*` symbols, add `build_video_abuse_report_reasons_list_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `video_abuse_report_reasons.py` cohesive, keep Layer 1 changes narrow, and avoid changes to `videos_reportAbuse`, comments, moderation, localization infrastructure, analytics, recommendations, search, or higher-level workflow modules.

## Risk and Mitigation

- **Input-boundary risk**: The local Layer 1 wrapper requires `part` plus `hl`. The public Layer 2 tool must keep that boundary explicit and reject undocumented selectors, report payloads, video identifiers, and other modifiers before execution.
- **Localization risk**: Callers may expect translated labels to always exist. Results must preserve requested `hl` context and returned fields without fabricating translations or treating empty results as failed lookups.
- **Quota risk**: Each invocation costs 1 quota unit. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `1`.
- **Access risk**: The endpoint uses API-key access expectations. The handler must not expose API keys or authorization details and must distinguish missing or invalid access from malformed input and upstream failure.
- **Empty-result risk**: Valid requests may return zero reason items. Result mapping must keep empty success distinct from validation, access, quota, and upstream failures.
- **Scope risk**: Do not add video abuse report submission, report status lookup, moderation action, policy adjudication, ranking, summarization, enrichment, analytics, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, or examples.
- **Cohesion risk**: `videoAbuseReportReasons_list` should live in the new `video_abuse_report_reasons` Layer 2 module, not in videos, comments, moderation, localization infrastructure, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_video_abuse_report_reasons_contract.py tests/unit/test_youtube_video_abuse_report_reasons.py tests/integration/test_youtube_video_abuse_report_reasons_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
