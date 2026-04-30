# Contract: YT-133 Layer 1 `playlistItems.insert` Auth and Write Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, writable-part support, required create inputs, optional-field boundaries, and normalized failure interpretation for the internal `playlistItems.insert` wrapper.

## Authorized Access Expectations

- Supported `playlistItems.insert` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, and secret-backed values must not appear in docs, tests, or logs

## Supported Write Boundary

The minimum supported creation request for this slice must make visible:

- the required writable `part`
- the required writable `body` payload
- the required playlist assignment inside the writable payload
- the required referenced resource inside the writable payload

The contract must clearly state whether the wrapper guarantees support only for the minimum playlist/video assignment path or also supports optional placement or content-details write fields.

If optional writable fields such as placement or content-details inputs are not explicitly supported in this slice, the wrapper contract must describe them as outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `part`
- requests missing the writable payload
- requests missing the target playlist identifier
- requests missing the referenced resource identifier
- requests that use unsupported writable parts
- requests that include unsupported writable fields or malformed nested write data
- requests that rely on incompatible authorization

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- normalized upstream create failures caused by playlist-, video-, or policy-specific rejection after execution begins
- successful playlist-item creation outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, or surfaced as an upstream rejection.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify the required writable create inputs in under 1 minute
- determine whether optional placement or content-details fields are supported or intentionally outside scope
- distinguish invalid-request rules from access and upstream failure boundaries

Expected validation coverage includes:

- unit tests for writable-input validation and OAuth-only enforcement
- integration tests for successful authorized creation and normalized failure propagation
- contract tests for auth guidance, write-boundary wording, and review-surface completeness
- transport tests confirming write requests preserve the declared endpoint identity and body-handling shape

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `50` visible alongside auth and write-boundary guidance
- New or changed Python functions involved in auth or write validation must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, and observability hooks outside the intentional endpoint addition
