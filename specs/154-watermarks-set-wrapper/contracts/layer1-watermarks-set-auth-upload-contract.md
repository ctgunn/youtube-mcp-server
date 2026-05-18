# Contract: YT-154 Layer 1 `watermarks.set` Auth and Upload Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, target-channel behavior, watermark resource metadata, media-upload constraints, unsupported-input boundaries, successful acknowledgement semantics, and normalized failure interpretation for the internal `watermarks.set` wrapper.

## Authorized Access Expectations

- Supported `watermarks.set` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, secret-backed values, channel-owner identity, delegated-owner credentials, and uploaded media bytes must not appear in docs, tests, logs, normalized results, or summaries

## Supported Upload Boundary

The minimum supported watermark-set request for this slice must make visible:

- the required target channel identifier through `channelId`
- the required watermark resource metadata through `body`
- the required upload content through `media`
- the documented maximum media size of 10 MB
- the documented accepted media MIME types: `image/jpeg`, `image/png`, and `application/octet-stream`
- the fact that a successful upstream watermark update has no body and must be normalized for downstream interpretation
- the optional partner-only `onBehalfOfContentOwner` parameter as either explicitly supported or explicitly outside the guaranteed request boundary

For this slice, bulk watermark setting, metadata-only requests, media-only requests, implicit channel discovery, and undocumented request fields are outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `channelId`
- requests whose `channelId` is blank or not a string-like channel identifier
- requests missing watermark resource metadata
- requests with incomplete or unsupported watermark timing, position, target-channel, or display metadata according to the final wrapper boundary
- requests missing `media`
- requests with unsupported media MIME types
- requests whose media content exceeds the documented 10 MB maximum when determinable locally
- requests that include unsupported top-level query fields
- requests that rely on incompatible authorization
- partner-only delegated content-owner inputs when the final wrapper contract does not explicitly support them

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- unsupported media failures caused by missing, unsupported, oversized, or invalid image content
- upstream image validation failures such as unsupported image format, excessive image height, excessive image width, or missing media body
- normalized forbidden failures caused by insufficient channel ownership, permissions, policy state, invalid channel context, or other watermark restrictions after execution begins
- normalized upstream unavailability failures after execution begins
- successful watermark-update acknowledgement outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, adjusted with different media content, retried later because of upstream availability, or surfaced as an upstream refusal.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify required `channelId`, `body`, and `media` inputs in under 1 minute
- determine the documented media size and MIME type boundaries
- determine whether delegated content-owner query behavior is supported or outside this slice
- distinguish invalid-request rules from access, unsupported media, upstream image validation, forbidden channel, upstream failure, and successful acknowledgement boundaries

Expected validation coverage includes:

- unit tests for target channel validation, watermark metadata validation, media payload validation, and OAuth-only enforcement
- integration tests for successful authorized watermark acknowledgement and normalized failure propagation
- contract tests for auth guidance, upload-boundary wording, and review-surface completeness
- transport tests confirming watermark-set requests preserve the declared endpoint identity, supported query shape, OAuth access, upload content handling, and 204-success acknowledgement behavior

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `50` visible alongside auth and upload-boundary guidance
- New or changed Python functions involved in auth, watermark request validation, upload validation, or result normalization must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, retry behavior, and observability hooks outside the intentional endpoint addition
