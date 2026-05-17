# Contract: YT-153 Layer 1 `videos.delete` Auth and Delete Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, target-video delete behavior, unsupported-input boundaries, successful acknowledgement semantics, and normalized failure interpretation for the internal `videos.delete` wrapper.

## Authorized Access Expectations

- Supported `videos.delete` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, secret-backed values, target-owner identity, and delegated-owner credentials must not appear in docs, tests, logs, or normalized summaries

## Supported Delete Boundary

The minimum supported delete request for this slice must make visible:

- the required target video identifier through `id`
- the destructive nature of the operation
- the fact that the request must not include a body
- the fact that a successful upstream delete acknowledgement has no body and must be normalized for downstream interpretation
- the optional partner-only `onBehalfOfContentOwner` parameter as either explicitly supported or explicitly outside the guaranteed request boundary

For this slice, bulk deletion, body-driven deletion, implicit target discovery, and undocumented request fields are outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `id`
- requests whose `id` is blank or not a string-like target identifier
- requests that include a request body
- requests that include unsupported top-level query fields
- requests that rely on incompatible authorization
- partner-only delegated content-owner inputs when the final wrapper contract does not explicitly support them

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- normalized forbidden delete failures caused by insufficient ownership, permissions, policy state, or other deletion restrictions after execution begins
- normalized video-not-found failures caused by missing, unavailable, or already absent target videos
- normalized upstream unavailability failures after execution begins
- successful deletion acknowledgement outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, treated as a missing target, retried later because of upstream availability, or surfaced as an upstream refusal.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify required `id` input in under 1 minute
- determine that request bodies are not part of the supported delete request
- determine whether delegated content-owner query behavior is supported or outside this slice
- distinguish invalid-request rules from access, forbidden, video-not-found, upstream failure, and successful acknowledgement boundaries

Expected validation coverage includes:

- unit tests for target identifier validation and OAuth-only enforcement
- integration tests for successful authorized delete acknowledgement and normalized failure propagation
- contract tests for auth guidance, delete-boundary wording, and review-surface completeness
- transport tests confirming delete requests preserve the declared endpoint identity, supported query shape, OAuth access, no-body behavior, and 204-success acknowledgement behavior

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `50` visible alongside auth and delete-boundary guidance
- New or changed Python functions involved in auth or delete request validation must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, retry behavior, and observability hooks outside the intentional endpoint addition
