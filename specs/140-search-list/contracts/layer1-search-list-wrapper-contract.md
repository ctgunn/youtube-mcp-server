# Contract: YT-140 Layer 1 `search.list` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `search.list` endpoint so maintainers can review endpoint identity, quota behavior, quota caveat handling, supported search refinements, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `search.list`
- Maintainer-visible endpoint identity and quota cost
- Maintainer-visible quota caveat for the existing `search` metadata example
- Supported request-shape and search-refinement boundary rules
- Review surfaces used by later search-dependent planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `search.list` wrapper must expose:

- `resource_name` as `search`
- `operation_name` as `list`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- `auth_condition_note`
- `lifecycle_state`
- `caveat_note`
- maintainer-facing notes describing supported search refinements and unsupported-request expectations

Maintainer-facing review surfaces should also keep the minimum search boundary visible, including the requirement that valid requests include `part` and `q`, the high-cost quota of `100`, and the fact that some search paths are public while others require stronger authorization.

The implemented review surface should make supported refinements reviewable in one pass, including pagination fields, date filters, language or region filters, restricted filters such as `forMine`, and video-only refinements that depend on `type=video`.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `100` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request fields are required for the baseline supported search path
- which optional refinements are intentionally supported in this slice
- that `type` is a first-class refinement affecting compatible request combinations
- how `pageToken` and `maxResults` behave for continuation and result-count control
- how `publishedAfter` and `publishedBefore` narrow results by time
- how `regionCode` and `relevanceLanguage` scope search results
- which restricted filters move the request into the stronger-authorization path
- which extra or incompatible field combinations are outside the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required search inputs, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid supported requests that return matches are successful
- valid supported requests that return no matches are also successful
- invalid request shapes or unsupported combinations are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must also make it possible for later layers to distinguish an authorization-constrained search request from an `invalid_request` failure or an upstream search failure returned after execution begins.

Successful normalized results must keep enough request context visible for later layers to tell which search request produced the result set and whether pagination can continue.

That visible result context should include the effective search query, the normalized `queryContext`, the selected search type when present, the next-page cursor when present, and whether the request stayed on the public path or moved into the restricted path.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `search.list` in one review pass
- find the quota cost of `100` without leaving the repository artifacts
- understand the known quota caveat without re-reading external documentation
- understand when API-key access is sufficient and when stronger authorization is required
- understand the supported search refinements and unsupported-request boundaries
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-refinement artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, required search inputs, refinement handling, and conditional-auth behavior
- consumer-facing checks showing higher layers can summarize `search.list` contract details without losing quota, caveat, auth, or refinement visibility

## Invariants

- YT-140 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, API keys, and OAuth tokens must never appear in contract artifacts, tests, or logs
