# Implementation Plan: Layer 2 Tool `subscriptions_delete`

**Branch**: `243-subscriptions-delete` | **Date**: 2026-07-20 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `subscriptions_delete` for the YouTube endpoint operation `subscriptions.delete`. The implementation will extend the existing subscriptions Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, reuse the existing Layer 1 `build_subscriptions_delete_wrapper()` from YT-143, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth disclosure, request validation, near-raw mutation acknowledgment shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and narrow: it requires a non-empty subscription relationship `id`, costs 50 official quota units per call, requires OAuth-backed user authorization, returns a deletion acknowledgment with safe target context, and does not add subscription listing, creation, lookup, channel search, recommendation, notification management, analytics, ranking, summarization, enrichment, bulk deletion, idempotency, preflight lookup, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing concrete Layer 2 subscriptions module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`; existing Layer 1 `subscriptions.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, deletion acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including subscriptions delete contract builders, descriptor builders, handler builders, argument validators, OAuth-context helpers, deletion context helpers, mutation acknowledgment mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single subscription delete request performs one Layer 1 wrapper call and local validation proportional only to supplied fields; no subscription lookup, list traversal, create behavior, channel enrichment, notification management, analytics, ranking, summarization, recommendation, bulk deletion, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint delete semantics, expose quota cost 50 in metadata/description/examples, declare OAuth requirement, require a non-empty `id`, reject unsupported fields and out-of-scope modifiers before execution, avoid leaking credential material or raw diagnostics in results or errors, add delete code under the existing `youtube_common` subscriptions family placement, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`subscriptions_delete`), additive changes to the existing subscriptions Layer 2 resource-family module, narrow public exports and default registry integration, replacement or superseding of any representative catalog placeholder if present, focused contract/unit/integration coverage, and documentation artifacts for YT-243 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-143 wrapper, YT-243 seed, sibling Layer 2 mutation tools, and current subscriptions Layer 2 module agree on quota cost `50`, required OAuth-backed access, required non-empty `id`, near-raw deletion acknowledgment behavior, and distinct validation/access/target-state/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `subscriptions_delete` contract builder, descriptor builder, handler builder, argument validator, OAuth-context helper, deletion context helper, result mapper, upstream-error mapper, local default transport/executor helper, default registration helper if touched, public export helper if touched, catalog/example helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `id`, empty `id`, non-string `id`, unsupported request fields, channel-id lookup attempts, body/create-shape attempts, notification modifiers, analytics/enrichment modifiers, missing OAuth, already-removed or missing targets, non-removable targets, quota failures, upstream invalid requests, authorization failures, endpoint unavailable, deprecated endpoint behavior, mutation acknowledgment shaping, safe deletion context, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── subscriptions_delete.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── subscriptions.py      # Existing Layer 1 delete wrapper dependency from YT-143
├── tools/
│   ├── dispatcher.py         # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py       # Public exports for subscriptions_delete symbols
│       ├── contracts.py      # Existing shared contract primitives
│       ├── examples.py       # Representative shared contract set, if catalog export requires update
│       ├── families.py       # Existing subscriptions family placement metadata
│       └── subscriptions.py  # Existing Layer 2 subscriptions family; add delete contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `subscriptions.py` Layer 2 family module because YT-241 and YT-242 already established the public subscriptions family, the Layer 1 dependency lives under the same resource-family name, and this slice should remain separate from channels, search, notifications, analytics, and higher-level workflow modules. This keeps `subscriptions_delete` cohesive with `subscriptions_list` and `subscriptions_insert` while avoiding a broad refactor.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `subscriptions.delete` quota, OAuth mode, required `id`, deletion acknowledgment shape, already-removed or missing target behavior, non-removable target behavior, and documented error categories.
- Confirm existing YT-143 Layer 1 wrapper availability and whether the public YT-243 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, access, mutation result, error, availability, and example conventions in the local codebase.
- Confirm current YT-241/YT-242 subscriptions Layer 2 family placement so `subscriptions_delete` extends the existing module rather than creating a second subscriptions family.
- Confirm how to add or replace any representative `subscriptions_delete` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing mutation tools, especially `subscriptions_insert`, `playlists_delete`, `playlistItems_delete`, `playlistImages_delete`, `channelSections_delete`, `comments_delete`, and the shared resource-family registry, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported deletion input shape, OAuth handling, subscriptions family placement, registration surface, deletion acknowledgment shape, safe error categories, examples, mutation-warning text, already-removed/missing/non-removable target caveats, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into subscription listing, creation, lookup, channel search, recommendation, notification management, analytics, ranking, summarization, enrichment, idempotency, preflight lookup, bulk deletion, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/data-model.md)
- [contracts/subscriptions_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/contracts/subscriptions_delete.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, mutation acknowledgment result shape, OAuth and quota caveats, `id` validation, unsupported modifier rejection, deletion warning, already-removed/missing/non-removable target caveats, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `subscriptions_delete`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth disclosure, quota accuracy, identifier validation, mutation acknowledgment behavior, deletion context, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Delete a Subscription Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `subscriptions_delete` is absent until implemented, requires a non-empty `id`, requires OAuth-backed access, invokes the Layer 1 delete wrapper once, and maps success to a deletion acknowledgment with endpoint, quota cost 50, requested id context, OAuth context, and any safe returned acknowledgment fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local delete transport, default executor, public exports, and dispatcher registration needed for successful subscription deletion.

**Refactor**: Align naming, docstrings, helper reuse, mutation caveats, OAuth handling, deletion context, and error mapping with `subscriptions_list`, `subscriptions_insert`, delete-style resource tools, and shared mutation-result conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Delete Semantics, Cost, and OAuth Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth requirement, required `id`, deletion acknowledgment result shape, mutation warning, already-removed/missing/non-removable target caveats, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful subscription deletion, missing id, empty id, unsupported field, missing authorization, already-removed or missing target, non-removable target, quota or upstream service failure, and out-of-scope subscription-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required id, mutation warning, target-state caveats, and unsupported-input guidance reviewable in `subscriptions.py`.

### User Story 3 - Reject Invalid, Missing, or Under-Authorized Delete Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, empty `id`, non-string `id`, unsupported top-level fields, channel-id lookup attempts, body/create-shape attempts, notification management modifiers, analytics/enrichment modifiers, missing OAuth, already-removed or missing target, not-owned target, blocked or non-removable target, quota failure, endpoint unavailable, upstream invalid request, deprecated behavior, and unexpected upstream failure.

**Green**: Implement validator, OAuth-context selection, deletion-context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_subscriptions_contract.py`, `tests/integration/test_youtube_subscriptions_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `SUBSCRIPTIONS_DELETE_*` symbols, add `build_subscriptions_delete_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `subscriptions.py` cohesive, keep Layer 1 changes narrow, and avoid changes to subscription list/insert, channels, search, notifications, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Mutation safety risk**: Successful calls delete user-visible subscription relationships for the authorized account. Metadata, usage notes, examples, quickstart, and result context must make deletion behavior visible before invocation.
- **OAuth risk**: Subscription deletion requires eligible OAuth-backed user authorization. The handler must reject missing or insufficient OAuth before execution and must not expose tokens in results, errors, logs, or examples.
- **Identifier risk**: The tool requires a subscription relationship `id`, not a channel id or search term. Validation and examples must prevent callers from assuming lookup, inference, bulk deletion, or preflight behavior.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Already-removed risk**: Retrying after a timeout or unclear upstream outcome may receive a missing/already-removed target failure. The public contract must document that this tool does not add idempotency, duplicate lookup, or preflight verification behavior.
- **Non-removable target risk**: Missing ownership, blocked relationships, policy restrictions, account state, or visibility limitations can reject validly shaped requests. Safe error mapping must keep these outcomes distinct from local validation and missing OAuth.
- **Scope risk**: Do not add subscription listing, creation, channel search, recommendation, notification management, analytics, ranking, summarization, enrichment, idempotency, preflight lookup, bulk deletion, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, channel owner details, or secret-bearing details in failures, logs, metadata, or examples.
- **Cohesion risk**: `subscriptions_delete` should live in the existing `subscriptions` Layer 2 module, not in channels, search, notification, analytics, retrieval, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
