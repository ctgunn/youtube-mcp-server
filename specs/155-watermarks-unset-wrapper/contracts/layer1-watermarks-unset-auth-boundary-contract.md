# Contract: YT-155 Layer 1 `watermarks.unset` Auth and Removal Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, target-channel behavior, unsupported payload boundaries, successful acknowledgement semantics, no-removal-possible semantics, and normalized failure interpretation for the internal `watermarks.unset` wrapper.

## Authorized Access Expectations

- Supported `watermarks.unset` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, secret-backed values, channel-owner identity, delegated-owner credentials, and unrelated media payloads must not appear in docs, tests, logs, normalized results, or summaries

## Supported Removal Boundary

The minimum supported watermark-unset request for this slice must make visible:

- the required target channel identifier through `channelId`
- the absence of required watermark metadata
- the absence of required upload content
- the fact that a successful upstream watermark removal has no body and must be normalized for downstream interpretation
- the optional partner-only `onBehalfOfContentOwner` parameter as either explicitly supported or explicitly outside the guaranteed request boundary
- the possibility that the target channel has no removable watermark or that upstream reports an already-removed/not-found state

For this slice, bulk watermark removal, upload-oriented requests, metadata-oriented requests, implicit channel discovery, and undocumented request fields are outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `channelId`
- requests whose `channelId` is blank or not a string-like channel identifier
- requests that include `body` watermark metadata
- requests that include `media` upload content
- requests that include watermark timing, position, upload, or set-only fields
- requests that include unsupported top-level query fields
- requests that rely on incompatible authorization
- partner-only delegated content-owner inputs when the final wrapper contract does not explicitly support them

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- unsupported payload failures caused by set-only metadata or upload content on unset requests
- normalized forbidden failures caused by insufficient channel ownership, permissions, policy state, invalid channel context, or other watermark restrictions after execution begins
- no-removal-possible outcomes caused by no current watermark, already removed state, or not-found response
- normalized upstream unavailability failures after execution begins
- successful watermark-removal acknowledgement outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, retried later because of upstream availability, or surfaced as a no-removal/forbidden upstream refusal.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify required `channelId` input in under 1 minute
- determine that `body` and `media` inputs are unsupported for unset
- determine whether delegated content-owner query behavior is supported or outside this slice
- distinguish invalid-request rules from access, unsupported payload, forbidden channel, no-removal, upstream failure, and successful acknowledgement boundaries

Expected validation coverage includes:

- unit tests for target channel validation, unsupported payload rejection, and OAuth-only enforcement
- integration tests for successful authorized watermark acknowledgement and normalized failure propagation
- contract tests for auth guidance, no-upload boundary wording, and review-surface completeness
- transport tests confirming watermark-unset requests preserve the declared endpoint identity, supported query shape, OAuth access, no-upload request handling, and 204-success acknowledgement behavior

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `50` visible alongside auth and removal-boundary guidance
- New or changed Python functions involved in auth, watermark request validation, or result normalization must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, retry behavior, and observability hooks outside the intentional endpoint addition
