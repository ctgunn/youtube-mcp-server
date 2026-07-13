# Implementation Plan: Layer 2 Tool `subscriptions_list`

**Branch**: `241-subscriptions-list` | **Date**: 2026-07-13 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `subscriptions_list` for the YouTube endpoint operation `subscriptions.list`. The implementation will add the concrete subscriptions Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, reuse the existing Layer 1 `build_subscriptions_list_wrapper()` from YT-141, and follow YT-201/YT-202 shared contract conventions for naming, quota, conditional auth disclosure, request validation, near-raw list result shaping, safe errors, examples, public exports, catalog replacement, and default registry integration.

The tool remains endpoint-backed and narrow: it requires `part` plus exactly one supported selector from `channelId`, `id`, `mine`, `myRecentSubscribers`, or `mySubscribers`, costs 1 official quota unit per call, supports `pageToken`, `maxResults`, and `order` within the selected list mode, treats `mine`, `myRecentSubscribers`, and `mySubscribers` as OAuth-backed user-context selectors, returns subscription list records with selector and paging context, and does not add subscription creation, deletion, partner-only delegation, channel enrichment, subscriber analytics, ranking, summarization, recommendation, or cross-endpoint aggregation.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; new concrete Layer 2 subscriptions module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`; existing Layer 1 `subscriptions.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, subscription list mappings, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including subscriptions list contract builders, descriptor builders, handler builders, selector validators, auth-path helpers, result mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, representative catalog helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single subscription list request performs one Layer 1 wrapper call and local validation proportional only to submitted fields and returned item count; no subscription mutation, channel enrichment, subscriber analytics, ranking, summarization, recommendation, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint list semantics, expose quota cost 1 in metadata/description/examples, declare conditional public or OAuth-backed access, require exactly one supported selector, reject unsupported or incompatible selector/pagination/order combinations before execution, avoid leaking credential material or raw diagnostics in results or errors, add concrete code under the existing `youtube_common` subscriptions family placement, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`subscriptions_list`), a new concrete subscriptions Layer 2 resource-family module, narrow public exports and default registry integration, replacement or superseding of any current representative `subscriptions_list` catalog placeholder, focused contract/unit/integration coverage, and documentation artifacts for YT-241 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-141 wrapper, YT-241 seed, project PRD/tool-spec inventory, and current official endpoint reference agree on quota cost `1`, required `part`, supported selectors, OAuth-backed user-context selectors, pagination, order, near-raw list results, and distinct validation/access/upstream-failure behavior. Partner-only delegation parameters and `forChannelId` are not part of this slice because they are absent from the seed and local Layer 1 wrapper contract.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `subscriptions_list` contract builder, descriptor builder, handler builder, argument validator, selector helper, auth-path helper, result mapper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, missing selector, conflicting selectors, OAuth-only selector without OAuth, public selector with wrong auth path, invalid paging, unsupported order, paging/order with identifier lookups where unsupported by the Layer 1 contract, empty successful results, quota failures, account closed or suspended, subscription forbidden, subscriber not found, upstream unavailable, safe error detail sanitization, and no fabricated enrichment.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── subscriptions_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── subscriptions.py      # Existing Layer 1 subscriptions.list wrapper dependency from YT-141
├── tools/
│   ├── dispatcher.py         # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py       # Public exports for subscriptions_list symbols
│       ├── contracts.py      # Existing shared contract primitives
│       ├── examples.py       # Replace/supersede any representative subscriptions_list catalog entry if required
│       ├── families.py       # Existing subscriptions family placement metadata
│       └── subscriptions.py  # New Layer 2 subscriptions family; add contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_subscriptions_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_subscriptions_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_subscriptions.py
```

**Structure Decision**: Add the concrete `subscriptions.py` Layer 2 family module because `families.py` already reserves the `subscriptions` family and no public `src/mcp_server/tools/youtube_common/subscriptions.py` module exists yet. This keeps `subscriptions_list` cohesive with the Layer 1 subscriptions wrapper, avoids mixing subscription listing behavior into channels/search/higher-level modules, and creates the expected contract/unit/integration test locations for the subscriptions family.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `subscriptions.list` quota, required `part`, supported selector modes, conditional auth behavior, pagination/order inputs, empty-result handling, and documented error categories.
- Confirm existing YT-141 Layer 1 wrapper availability and whether the public YT-241 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, list result, error, availability, and example conventions in the local codebase.
- Confirm how to add or replace any representative `subscriptions_list` entry in shared examples/catalog once a concrete endpoint-backed subscriptions family exists.
- Compare existing list-style tools, especially `playlists_list`, `search_list`, `playlistItems_list`, `commentThreads_list`, `comments_list`, and `channels_list`, to choose the smallest consistent implementation shape.
- Confirm official endpoint reference details that affect public-facing contract text: quota cost, required parts, exactly-one filter selectors, OAuth-only selectors, page-size bounds, order values, response shape, and safe error categories.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, conditional auth handling, subscriptions family placement, registration surface, list result shape, safe error categories, examples, empty-result behavior, partner-only exclusions, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into subscription mutation, partner delegation, channel enrichment, subscriber analytics, ranking, summarization, recommendation, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/data-model.md)
- [contracts/subscriptions_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/contracts/subscriptions_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, list result shape, conditional auth and quota caveats, selector exclusivity, pagination/order validation, empty-result success, safe error categories, and no-enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `subscriptions_list`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, conditional access disclosure, quota accuracy, selector validation, list result behavior, empty-result behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - List Channel Subscriptions

**Red**: Add failing contract/unit/integration checks proving `subscriptions_list` is absent as a concrete endpoint-backed tool until implemented, requires `part` plus exactly one supported selector, invokes the Layer 1 subscriptions wrapper once with the correct auth path, and maps success to a near-raw subscription list result with endpoint, quota cost 1, selector context, auth path, paging context, and returned items.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, conditional-auth default local executor, public exports, and dispatcher registration needed for successful public and OAuth-backed subscription listing requests.

**Refactor**: Align naming, docstrings, helper reuse, selector caveats, empty-result handling, and error mapping with existing list tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Filters, and Auth Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, conditional auth disclosure, required `part`, supported selector modes, supported `pageToken`, `maxResults`, and `order`, availability state, empty-result behavior, private subscriber limitations, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for channel subscriptions, direct subscription lookup, current-user subscriptions, recent subscribers, subscriber list, paginated traversal, ordered collection request, empty successful result, validation failures, missing authorization, quota or upstream service failure, and out-of-scope enrichment or mutation request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific required inputs, quota, conditional auth, selector compatibility, pagination, ordering, private subscriber caveats, empty-result, no-enrichment, and unsupported-input guidance reviewable in `subscriptions.py`.

### User Story 3 - Reject Ambiguous or Invalid Selector Combinations

**Red**: Add failing validation and error-mapping checks for missing `part`, invalid `part`, missing selector, conflicting selectors, false-only boolean selectors, OAuth-backed selector without OAuth, public selector with OAuth-only auth path, unsupported fields, invalid page token, out-of-range `maxResults`, unsupported `order`, paging/order with direct `id` lookup where unsupported by the Layer 1 contract, quota failure, account closed, account suspended, subscription forbidden, subscriber not found, endpoint unavailable, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, API keys, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_subscriptions_contract.py`, `tests/integration/test_youtube_subscriptions_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `SUBSCRIPTIONS_LIST_*` symbols, add `build_subscriptions_list_tool_descriptor()` to the default registry, add concrete representative contract/example coverage, and replace or supersede any current placeholder `subscriptions_list` catalog entry so the catalog represents the endpoint-backed tool.

**Refactor**: Keep `subscriptions.py` cohesive, keep Layer 1 changes narrow, and avoid changes to subscription insert/delete, channels, search, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Quota risk**: Each invocation costs 1 quota unit. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `1`.
- **Auth path risk**: `channelId` and `id` are public-compatible lookup paths while `mine`, `myRecentSubscribers`, and `mySubscribers` require OAuth-backed user context. Validation and examples must distinguish missing auth from invalid input and public empty results.
- **Selector compatibility risk**: The endpoint requires exactly one supported selector. Local validation must reject missing or conflicting selectors before execution.
- **Pagination and order risk**: Page tokens, page size, and ordering must stay tied to compatible collection lookups and must not imply cross-selector token reuse.
- **Private subscriber risk**: Subscriber-list modes may be limited by platform visibility or account state. The result contract must distinguish successful limited/empty results from authorization and upstream failures.
- **Response-boundary risk**: Subscription list responses return subscription resources, not hydrated channel analytics, subscriber profiles, recommendations, or summaries. The result mapper must not fabricate enrichment.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, or secret-bearing details in failures, logs, metadata, or examples.
- **Cohesion risk**: `subscriptions_list` should live in the new concrete `subscriptions` Layer 2 module, not in channels, search, retrieval, analytics, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
