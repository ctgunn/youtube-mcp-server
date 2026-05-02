# Contract: YT-138 Layer 1 `playlists.update` Auth and Write Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, writable-part support, required update inputs, optional-field boundaries, and normalized failure interpretation for the internal `playlists.update` wrapper.

## Authorized Access Expectations

- Supported `playlists.update` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, and secret-backed values must not appear in docs, tests, or logs

## Supported Write Boundary

The minimum supported update request for this slice must make visible:

- the required writable `part`
- the required playlist identifier in the update body
- the required writable `body.snippet` payload
- the required playlist title inside the writable payload
- the fact that `part=snippet` is the only guaranteed writable-part combination in this slice

The contract must clearly state whether the wrapper guarantees support only for the minimum identifier-plus-title update path or also supports optional writable fields such as description, status, or localization updates.

If optional writable fields such as `body.snippet.description`, `body.status`, or `body.localizations` are not explicitly supported in this slice, the wrapper contract must describe them as outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `part`
- requests missing the writable payload
- requests missing the target playlist identifier
- requests missing the writable `snippet`
- requests missing the required playlist title
- requests that use unsupported writable parts
- requests that include unsupported writable fields or malformed nested write data
- requests that rely on incompatible authorization

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- normalized upstream update failures caused by missing targets, policy restrictions, or other upstream rejection after execution begins
- successful playlist update outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, or surfaced as an upstream rejection.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify the required identifier and writable update inputs in under 1 minute
- determine whether optional description, status, or localization fields are supported or intentionally outside scope
- distinguish invalid-request rules from access and upstream failure boundaries

Expected validation coverage includes:

- unit tests for writable-input validation and OAuth-only enforcement
- integration tests for successful authorized update and normalized failure propagation
- contract tests for auth guidance, write-boundary wording, and review-surface completeness
- transport tests confirming write requests preserve the declared endpoint identity and body-handling shape

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `50` visible alongside auth and write-boundary guidance
- New or changed Python functions involved in auth or write validation must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, and observability hooks outside the intentional endpoint addition
