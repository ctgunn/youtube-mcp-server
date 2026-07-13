# Research: YT-241 Layer 2 Tool `subscriptions_list`

## Decision: Add a concrete Layer 2 subscriptions resource-family module

**Rationale**: The seed slice requires public Layer 2 exposure of `subscriptions.list`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` already reserves the `subscriptions` resource family with expected module and test locations. No concrete `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py` module exists yet. The narrowest cohesive implementation is to add that module with constants, validation, list result mapping, contract metadata, examples, descriptor, handler, exports, and registry integration.

**Alternatives considered**:
- Add `subscriptions_list` to `channels.py` because subscriptions are channel relationships. Rejected because subscriptions are their own upstream resource family and should keep endpoint ownership clear.
- Keep only representative catalog coverage. Rejected because YT-241 requires a public endpoint-backed Layer 2 tool.
- Create a higher-level subscriber analysis tool. Rejected because analytics, summarization, recommendation, and research synthesis belong outside this low-level endpoint slice.

## Decision: Reuse the existing Layer 1 `build_subscriptions_list_wrapper()`

**Rationale**: The local Layer 1 wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py` already models `subscriptions.list` with resource `subscriptions`, method `list`, path `/youtube/v3/subscriptions`, quota cost `1`, conditional auth, required `part`, exactly-one selector behavior, public-compatible `channelId` and `id` selectors, OAuth-backed `mine`, `myRecentSubscribers`, and `mySubscribers` selectors, pagination/order support, and successful empty-result guidance. Reusing it keeps upstream request execution, auth validation, quota metadata, and response normalization in the Layer 1 dependency rather than redefining a parallel upstream contract.

**Alternatives considered**:
- Duplicate request execution or upstream shaping in Layer 2. Rejected because Layer 2 should depend on Layer 1 wrappers and avoid duplicating execution, auth, quota, and upstream error behavior.
- Expand the Layer 1 wrapper during this slice. Rejected unless tests expose a missing export or metadata defect, because the YT-241 scope is the public Layer 2 tool.

## Decision: Require `part` plus exactly one supported selector

**Rationale**: The YT-141 wrapper, YT-241 seed, and current official endpoint reference all require `part` and a single filter/selector. The supported YT-241 selectors are `channelId`, `id`, `mine`, `myRecentSubscribers`, and `mySubscribers`. The Layer 2 contract should reject missing selectors, multiple selectors, false-only boolean selectors, blank selector values, and unsupported selector-like fields before execution.

**Alternatives considered**:
- Allow selector-free listing. Rejected because it conflicts with the endpoint contract and existing Layer 1 wrapper.
- Allow multiple selectors and let upstream choose behavior. Rejected because it creates ambiguous caller outcomes and risks quota-consuming invalid requests.
- Add convenience selectors not present in the seed or Layer 1 wrapper. Rejected because this slice must expose the supported Layer 1 contract, not broaden endpoint inventory.

## Decision: Model auth as conditional public or OAuth-backed access

**Rationale**: The supported public-compatible selectors are `channelId` and `id`; user-context selectors `mine`, `myRecentSubscribers`, and `mySubscribers` require OAuth-backed authorization. The public Layer 2 contract must disclose this before invocation so callers can distinguish public empty results, missing authorization, insufficient authorization, and private or unavailable subscription visibility.

**Alternatives considered**:
- Declare all subscription list calls API-key only. Rejected because user-context selectors require authenticated user context.
- Declare all subscription list calls OAuth-required. Rejected because the supported public selectors are intended for public-compatible lookup.
- Hide auth selection behind a generic access field. Rejected because callers need to reason about permissions and failure categories before spending quota.

## Decision: Preserve the supported subset from the seed and local wrapper

**Rationale**: The current official endpoint reference also documents partner-only delegation fields and `forChannelId`, but YT-241 and the local YT-141 wrapper define the supported Layer 2 surface as `part`, `channelId`, `id`, `mine`, `myRecentSubscribers`, `mySubscribers`, `pageToken`, `maxResults`, and `order`. Adding partner-only delegation or `forChannelId` in this slice would broaden scope beyond the seed-derived feature and require Layer 1 contract expansion first.

**Alternatives considered**:
- Add every current official optional parameter to Layer 2. Rejected because the authoritative slice and local dependency do not support them.
- Silently ignore unsupported official parameters. Rejected because unsupported fields should fail with actionable validation before execution.
- Document unsupported official parameters only in implementation comments. Rejected because public callers need clear out-of-scope guidance through tool metadata and examples.

## Decision: Validate pagination and order as selector-aware list controls

**Rationale**: The local wrapper notes that `pageToken`, `maxResults`, and `order` are collection-style controls. The public contract should support them for compatible collection requests, validate `maxResults` within official `0` to `50` bounds, reject blank page tokens, reject unsupported order values, and keep continuation tokens tied to the original selector context.

**Alternatives considered**:
- Permit pagination and ordering for every selector without local checks. Rejected because direct identifier lookup is not a collection traversal in the Layer 1 contract.
- Omit pagination from Layer 2. Rejected because pagination is part of the seed and endpoint list behavior.
- Add cursor persistence. Rejected because this feature has no feature-specific storage and can rely on caller-provided continuation tokens.

## Decision: Return a near-raw subscription list result with safe selector, auth, quota, and paging context

**Rationale**: `subscriptions.list` returns subscription resources and page metadata. The Layer 2 result should preserve returned upstream fields and add MCP-usable context such as endpoint identity, quota cost, selected selector, auth path, empty-result marker, and pagination tokens when present. It must not hydrate channel details, infer subscriber profiles, compute analytics, rank subscriptions, summarize subscribers, or generate recommendations.

**Alternatives considered**:
- Return only raw upstream output. Rejected because shared Layer 2 conventions require quota, auth, response, and error context for clients.
- Enrich each subscription item through channels or analytics. Rejected because it would add extra endpoint calls, quota consumption, and higher-level workflow behavior outside YT-241.
- Collapse empty collections into not-found errors. Rejected because an accessible request can legitimately return an empty collection.

## Decision: Map validation, access, quota, not-found, and upstream failures into safe categories

**Rationale**: Callers need to distinguish local validation failures from authentication failures, authorization failures, quota exhaustion, account state failures, missing subscribers, endpoint unavailability, and unexpected upstream failures. Error details must be sanitized so API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, and secret-bearing request context are never exposed.

**Alternatives considered**:
- Surface raw upstream errors directly. Rejected because the project requires safe MCP-facing errors and no secret leakage.
- Collapse all failures to `invalid_request`. Rejected because auth, quota, not-found, and availability failures require different caller action.
- Treat `subscriberNotFound` as an empty success. Rejected because it identifies a missing subscriber/request target, not merely an accessible empty result set.

## Decision: Follow existing Layer 2 list test/export patterns

**Rationale**: Existing Layer 2 list modules expose constants, input schemas, usage notes, caveats, examples, contract builders, handlers, descriptors, validators, result mappers, safe tool errors, public package exports, shared catalog entries, and default registry descriptors. YT-241 should add the same surfaces for `subscriptions_list` with focused contract, unit, integration, catalog, dispatcher, and scaffold coverage.

**Alternatives considered**:
- Add only integration tests. Rejected by the constitution and existing project practice because public tool contracts need unit, contract, and integration coverage.
- Add broad cross-resource refactors before implementing the tool. Rejected because this slice can be delivered by narrow additions to a new subscriptions family module plus exports and registration.

## Decision: Require reStructuredText docstrings for any new or changed Python functions

**Rationale**: The constitution requires every new or modified Python function to include a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. This applies to production helpers and test fake methods touched during implementation.

**Alternatives considered**:
- Rely on module-level documentation only. Rejected because the constitution specifically requires function-level docstrings for changed Python functions.
- Defer docstrings to cleanup without test or review evidence. Rejected because docstring compliance is a planning and review gate.

## Clarification Closure

All planning-time clarifications for YT-241 are resolved in this research artifact. No unresolved clarification markers remain.
