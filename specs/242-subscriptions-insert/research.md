# Research: YT-242 Layer 2 Tool `subscriptions_insert`

## Decision: Expose `subscriptions_insert` in the existing Layer 2 subscriptions resource family

**Rationale**: The seed slice requires public Layer 2 exposure of `subscriptions.insert`, and YT-241 already established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py` as the public subscriptions resource-family module. The narrowest cohesive implementation is to extend that module with insert-specific constants, validation, result mapping, contract metadata, examples, descriptor, handler, exports, and registry integration.

**Alternatives considered**:
- Add `subscriptions_insert` to channels or search modules. Rejected because those modules represent different upstream resources and would blur endpoint ownership.
- Create a second subscriptions insert-only module. Rejected because the existing subscriptions family already owns adjacent endpoint tools without a broad refactor.
- Modify Layer 1 only. Rejected because YT-142 already owns the internal `subscriptions.insert` wrapper and YT-242 is explicitly public Layer 2 work.

## Decision: Reuse the existing Layer 1 `build_subscriptions_insert_wrapper()`

**Rationale**: The local Layer 1 wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py` already models `subscriptions.insert` with resource `subscriptions`, method `insert`, `POST /youtube/v3/subscriptions`, quota cost `50`, OAuth-required auth, required `part`, required `body`, target-channel validation, and normalized target context in successful responses. Reusing it keeps upstream request execution, quota metadata, OAuth enforcement, and upstream error behavior in the Layer 1 dependency rather than redefining a parallel upstream contract.

**Alternatives considered**:
- Duplicate YouTube request shaping in Layer 2. Rejected because Layer 2 should depend on Layer 1 wrappers and avoid duplicating execution, auth, quota, and upstream error behavior.
- Expand the Layer 1 wrapper during this slice. Rejected unless tests expose a missing export or metadata defect, because the YT-242 scope is the public Layer 2 tool.

## Decision: Require `part=snippet` plus `body.snippet.resourceId.channelId`

**Rationale**: The YT-142 wrapper requires `part` and `body`, accepts only the writable `snippet` part, and requires the target channel at `body.snippet.resourceId.channelId`. It allows `body.snippet.resourceId.kind` only when the value is `youtube#channel` and rejects unsupported top-level body fields, extra snippet fields, and extra resource-id fields. The public Layer 2 contract should preserve that boundary so callers know which writable inputs create a subscription relationship and which optional write fields are unsupported unless deliberately added later.

**Alternatives considered**:
- Accept any upstream subscription resource body. Rejected because the local Layer 1 wrapper deliberately constrains the write surface for this slice.
- Make `part` optional with a default. Rejected because the wrapper and public contract need the caller to acknowledge the writable part selection.
- Support notification settings, subscriber details, or extra subscription snippet fields by default. Rejected because the Layer 1 wrapper marks these as unsupported write fields unless the contract is deliberately expanded.

## Decision: Model access as OAuth-required for all calls

**Rationale**: Subscription creation mutates the authorized account's subscription relationships and the Layer 1 wrapper requires OAuth-backed access. The Layer 2 contract must expose the OAuth requirement in metadata, descriptions, usage notes, examples, and safe error categories so callers can identify access needs before spending quota or attempting creation.

**Alternatives considered**:
- Allow API-key access for public subscription creation. Rejected because `subscriptions.insert` is a user-authorized mutation.
- Split authorization by request field. Rejected because the supported create operation requires OAuth for every valid request.

## Decision: Return a near-raw created-subscription mutation result with safe target context

**Rationale**: Layer 2 tools should remain close to upstream endpoint behavior while adding MCP-usable structure. The result should preserve returned subscription fields, requested part, target channel context, quota cost, auth mode, endpoint identity, and safe upstream failure categories without fabricating channel search, subscriber profiles, notification settings, analytics, ranking, recommendation, summarization, or enrichment data.

**Alternatives considered**:
- Return only raw upstream JSON. Rejected because shared Layer 2 conventions require quota, auth, response, and error context for clients.
- Enrich the created subscription with channel details, recommendations, subscriber status, notification settings, or analytics. Rejected because those workflows belong to separate endpoint or Layer 3 features.

## Decision: Document duplicate and ineligible-target caveats rather than adding preflight checks

**Rationale**: `subscriptions_insert` is a low-level endpoint-backed mutation. Duplicate relationships, self-subscription, blocked channels, missing channels, account-state restrictions, and policy restrictions can be rejected by the upstream service, and this slice does not include a higher-level preflight lookup or idempotency workflow. The contract should warn callers and categorize failures safely without adding extra endpoint calls.

**Alternatives considered**:
- Add duplicate detection before creation. Rejected because it would require extra endpoint calls and higher-level workflow semantics outside YT-242.
- Promise idempotent retry behavior. Rejected because the shared contract and upstream insert behavior do not provide that guarantee for this slice.

## Decision: Follow existing Layer 2 mutation test and export patterns

**Rationale**: Existing Layer 2 modules expose constants, input schemas, usage notes, caveats, examples, contract builders, handlers, descriptors, validators, result mappers, safe tool errors, public package exports, shared catalog entries, and default registry descriptors. YT-242 should add the same surfaces for `subscriptions_insert` with focused contract, unit, integration, catalog, dispatcher, and scaffold coverage.

**Alternatives considered**:
- Add only integration tests. Rejected by the constitution and existing project practice because public tool contracts need unit, contract, and integration coverage.
- Add broad cross-resource refactors before implementing the tool. Rejected because this slice can be delivered by narrow additions to the existing subscriptions family plus exports and registration.

## Decision: Require reStructuredText docstrings for any new or changed Python functions

**Rationale**: The constitution requires every new or modified Python function to include a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. This applies to production helpers and test fake methods touched during implementation.

**Alternatives considered**:
- Rely on module-level documentation only. Rejected because the constitution specifically requires function-level docstrings for changed Python functions.
- Defer docstrings to cleanup without test or review evidence. Rejected because docstring compliance is a planning and review gate.
