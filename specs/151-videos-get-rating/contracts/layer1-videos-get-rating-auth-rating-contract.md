# Contract: YT-151 Layer 1 `videos.getRating` Auth and Rating-State Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, supported identifier boundaries, returned rating-state semantics, unsupported-input boundaries, and normalized failure interpretation for the internal `videos.getRating` wrapper.

## Authorized Access Expectations

- Supported `videos.getRating` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, and secret-backed values must not appear in docs, tests, or logs

## Supported Identifier Boundary

The minimum supported lookup request for this slice must make visible:

- the required target video identifier input through `id`
- whether `id` may represent one target video, multiple target videos, or both for this slice
- that the supported multi-video form uses one comma-delimited `id` field with at most 50 video identifiers per request
- the fact that undocumented list-style or delegated modifiers remain outside the guaranteed request boundary unless explicitly documented later

If optional or undocumented request fields are not explicitly supported in this slice, the wrapper contract must describe them as outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Returned Rating-State Boundary

The wrapper must clearly document the successful returned state set for this slice, including:

- the successful positive-rating state
- the successful negative-rating state
- the successful unrated state used when the authorized viewer has not rated a requested video

Maintainer-facing artifacts should make the supported returned state vocabulary explicit as `liked`, `disliked`, and `none` so later layers do not need to infer meaning from raw upstream payloads.

The contract must make clear that unrated outcomes remain successful lookup results and are not to be conflated with failed lookups or missing data.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `id`
- requests whose identifier form falls outside the documented supported boundary
- requests that include unsupported or undocumented request fields
- requests that rely on incompatible authorization

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- normalized upstream lookup failures caused by missing targets, unavailable rating state, or other upstream refusal after execution begins
- normalized `upstream_unavailable` outcomes caused by temporary upstream rating-lookup unavailability after execution begins
- successful unrated lookup outcomes
- successful rated lookup outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, or surfaced as an upstream lookup failure.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify the required identifier input in under 1 minute
- determine what successful rating states may be returned for this slice
- distinguish invalid-request rules from access, upstream failure, and successful unrated-result boundaries

Expected validation coverage includes:

- unit tests for identifier validation and OAuth-only enforcement
- integration tests for successful authorized lookup and normalized failure propagation
- contract tests for auth guidance, returned-state wording, and review-surface completeness
- transport tests confirming lookup requests preserve the declared endpoint identity and supported identifier shape

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `1` visible alongside auth and rating-state guidance
- New or changed Python functions involved in auth or identifier validation must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, and observability hooks outside the intentional endpoint addition
