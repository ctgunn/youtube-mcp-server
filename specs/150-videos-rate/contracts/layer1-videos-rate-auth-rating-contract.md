# Contract: YT-150 Layer 1 `videos.rate` Auth and Rating Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, supported rating semantics, required request inputs, unsupported-input boundaries, and normalized failure interpretation for the internal `videos.rate` wrapper.

## Authorized Access Expectations

- Supported `videos.rate` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, and secret-backed values must not appear in docs, tests, or logs

## Supported Rating Boundary

The minimum supported rating request for this slice must make visible:

- the required target video identifier through `id`
- the required requested action through `rating`
- the supported action set of `like`, `dislike`, and `none`
- the fact that `none` is the supported clear-rating path for this slice

The contract must clearly state whether the wrapper guarantees support only for the bounded action set above or also supports optional or delegated modifiers.

If optional or undocumented request fields are not explicitly supported in this slice, the wrapper contract must describe them as outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `id`
- requests missing `rating`
- requests whose `rating` value is not one of the documented supported actions, including unsupported rating values
- requests that include unsupported or undocumented request fields
- requests that rely on incompatible authorization

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- normalized upstream rating failures caused by missing targets, policy restrictions, disabled rating, or other upstream rejection after execution begins
- successful rating acknowledgement outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, or surfaced as an upstream rejection.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify the required identifier and rating inputs in under 1 minute
- determine whether only `like`, `dislike`, and `none` are supported in this slice
- distinguish invalid-request rules from access and upstream failure boundaries

Expected validation coverage includes:

- unit tests for rating-input validation and OAuth-only enforcement
- integration tests for successful authorized rating and normalized failure propagation
- contract tests for auth guidance, action-boundary wording, and review-surface completeness
- transport tests confirming rating requests preserve the declared endpoint identity and supported input shape

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `50` visible alongside auth and rating-boundary guidance
- New or changed Python functions involved in auth or rating validation must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, and observability hooks outside the intentional endpoint addition
