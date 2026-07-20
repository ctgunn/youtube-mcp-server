# Research: Layer 2 Subscriptions Delete Tool

## Decision: Implement `subscriptions_delete` as the concrete Layer 2 tool for `subscriptions.delete`

**Rationale**: The YT-243 seed requires exposing `subscriptions.delete` as the low-level MCP tool named `subscriptions_delete`. The PRD requires one Layer 2 public tool per supported YouTube Data API resource method, using resource-method naming and near-direct endpoint semantics. The adjacent `subscriptions_list` and `subscriptions_insert` work already established the subscriptions Layer 2 resource-family module.

**Alternatives considered**: Add deletion behavior to `subscriptions_insert` or `subscriptions_list`; rejected because deletion is a distinct mutating endpoint and the spec explicitly excludes listing, creation, discovery, recommendation, analytics, notification management, and higher-level subscription workflows. Create a separate module for deletion; rejected because the existing `subscriptions` family module is the cohesive location for all Layer 2 subscription endpoint tools.

## Decision: Rely on the existing Layer 1 `build_subscriptions_delete_wrapper()`

**Rationale**: YT-143 already provides the Layer 1 `subscriptions.delete` wrapper, including endpoint identity, `DELETE /youtube/v3/subscriptions`, required `id`, OAuth-required auth, quota cost `50`, and target-state-sensitive deletion guidance. YT-243 should expose that capability publicly instead of redefining upstream behavior in Layer 2.

**Alternatives considered**: Implement a new direct upstream call inside Layer 2; rejected because Layer 2 tools must depend on Layer 1 wrappers for endpoint behavior. Change Layer 1 as part of YT-243; rejected unless implementation tests later reveal a narrow export or metadata gap.

## Decision: Support only `id` as the public deletion input

**Rationale**: The Layer 1 wrapper and feature spec identify the subscription relationship identifier as the required deletion input. Keeping the request shape to `{ "id": "..." }` preserves endpoint semantics, makes validation clear, and avoids implying search, lookup, bulk deletion, or idempotent preflight behavior.

**Alternatives considered**: Accept channel IDs, subscription resource bodies, target channel selectors, or lookup modifiers; rejected because those belong to list/search workflows or would require extra endpoint calls. Add bulk deletion; rejected because the endpoint-backed Layer 2 tool should remove one subscription relationship per call.

## Decision: Require OAuth-backed authorization for every `subscriptions_delete` call

**Rationale**: Subscription deletion mutates the authorized account's relationships. The seed requires OAuth requirements to be documented clearly, and the Layer 1 wrapper enforces OAuth-required access. Metadata, descriptions, examples, validation, and errors must make this visible before invocation.

**Alternatives considered**: Allow API-key access for public deletion; rejected because deletion is account-scoped mutation. Silently attempt deletion without OAuth and rely on upstream rejection; rejected because local validation should give safer and clearer feedback.

## Decision: Publish official quota cost `50` everywhere the caller evaluates the tool

**Rationale**: The YT-243 seed identifies official quota cost `50`. YT-202 requires quota visibility in metadata, descriptions, and examples. Result context should also carry quota cost so callers can audit successful and failed workflows.

**Alternatives considered**: Put quota only in shared metadata; rejected because the seed explicitly requires tool description/examples to document the cost. Defer quota to external documentation; rejected because clients must understand cost from discovery and contract artifacts alone.

## Decision: Return a deletion acknowledgment with safe request, quota, and auth context

**Rationale**: `subscriptions.delete` can produce an empty or acknowledgment-style upstream success response. The Layer 2 result should preserve endpoint identity, quota cost, requested subscription id, OAuth mode, and any safe returned upstream context without fabricating a deleted resource or channel details.

**Alternatives considered**: Return the deleted subscription resource; rejected because the delete endpoint does not guarantee full resource details. Return only `true`; rejected because callers need enough context to identify the operation and audit quota/access behavior.

## Decision: Map target-state and upstream failures into safe Layer 2 categories

**Rationale**: The spec requires clear distinctions between validation failures, access failures, already-removed or missing subscriptions, non-removable relationships, quota failures, invalid requests, unavailable service, deprecated behavior, and unexpected upstream failures. Existing subscription insert/list tools map normalized upstream categories to safe caller-facing categories while sanitizing credentials and raw diagnostics.

**Alternatives considered**: Pass through raw upstream failures; rejected because the constitution requires secure, deterministic, machine-readable outputs without secret or diagnostic leaks. Collapse all target-state failures into one generic error; rejected because callers need to distinguish correctable validation/access issues from missing or non-removable subscription targets.

## Decision: Extend existing subscriptions tests and registry coverage

**Rationale**: Existing coverage locations already cover the subscriptions family: `tests/contract/test_youtube_subscriptions_contract.py`, `tests/unit/test_youtube_subscriptions.py`, `tests/integration/test_youtube_subscriptions_registration.py`, plus common catalog and registration tests. Adding delete expectations there keeps the feature reviewable and follows the YT-201/YT-202 pattern.

**Alternatives considered**: Create a standalone delete-only test suite; rejected because it would duplicate family coverage and make shared catalog behavior harder to review. Use only unit tests; rejected by the constitution and spec, which require contract, integration, and full-suite validation.

## Decision: Require reStructuredText docstrings for all new or changed Python functions

**Rationale**: Constitution v1.2.0 requires every new or modified Python function to include a reStructuredText docstring covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. YT-243 implementation will likely add or change contract builders, descriptor builders, handlers, validators, result mappers, error mappers, default executor helpers, exports, and fake wrapper methods in tests.

**Alternatives considered**: Add docstrings only to public functions; rejected because the constitution applies to every new or changed Python function. Defer docstrings to review cleanup; rejected because docstrings are a planning and implementation gate.
