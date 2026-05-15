# Contract: YT-152 Layer 1 `videos.reportAbuse` Auth and Payload Boundary Contract

## Purpose

Define the maintainer-facing rules for authorized access, required abuse-report payload fields, supported optional payload fields, unsupported-input boundaries, successful acknowledgement semantics, and normalized failure interpretation for the internal `videos.reportAbuse` wrapper.

## Authorized Access Expectations

- Supported `videos.reportAbuse` requests require OAuth-backed access
- Maintainers must be able to determine the authorized-access requirement from wrapper metadata, docstrings, and feature-local contracts without reading transport code
- Missing or incompatible authorization must remain distinguishable from malformed request data
- Credentials, tokens, secret-backed values, and report submitter identity must not appear in docs, tests, logs, or normalized summaries

## Supported Payload Boundary

The minimum supported report request for this slice must make visible:

- the required report payload object through `body`
- the required target video identifier through `body.videoId`
- the required primary abuse reason through `body.reasonId`
- the supported optional secondary reason through `body.secondaryReasonId`
- the supported optional explanatory text through `body.comments`
- the supported optional language indicator through `body.language`
- the fact that a successful upstream report acknowledgement has no body and must be normalized for downstream interpretation

The contract must clearly state whether the wrapper guarantees support only for the bounded body fields above or also supports optional query modifiers.

For this slice, partner-only `onBehalfOfContentOwner` behavior and undocumented request fields are outside the guaranteed request boundary and require clear rejection or flagging when they are used.

## Request Validation Expectations

The wrapper must reject or clearly flag:

- requests missing `body`
- requests missing `body.videoId`
- requests missing `body.reasonId`
- requests whose body is not an object-like report payload
- requests that include unsupported or undocumented body fields
- requests that include unsupported or partner-only top-level query fields
- requests that rely on incompatible authorization

The request boundary must remain deterministic and must not silently rewrite malformed input into supported behavior.

## Failure Boundary Expectations

The wrapper must preserve distinct maintainer-visible meaning for:

- `invalid_request` outcomes caused by incomplete or unsupported request shapes
- access-related failures caused by missing or incompatible authorized access
- normalized upstream invalid abuse-reason failures caused by unexpected reason values or invalid primary/secondary reason combinations after execution begins
- normalized rate-limit failures caused by the reporter sending too many report requests in a timeframe
- normalized video-not-found failures caused by missing or unavailable target videos
- normalized upstream unavailability failures after execution begins
- successful report acknowledgement outcomes

Later layers must be able to infer from repository artifacts alone whether a failed request should be corrected locally, retried with different access, delayed because of rate limiting, or surfaced as an upstream refusal.

## Review Validation Expectations

Validation for this contract must prove that maintainers can:

- determine the endpoint is OAuth-required
- identify required `videoId` and `reasonId` inputs in under 1 minute
- determine which optional payload fields are supported for this slice
- determine that delegated content-owner query behavior is not guaranteed in this slice
- distinguish invalid-request rules from access, invalid reason, rate-limit, video-not-found, upstream failure, and successful acknowledgement boundaries

Expected validation coverage includes:

- unit tests for body validation and OAuth-only enforcement
- integration tests for successful authorized report acknowledgement and normalized failure propagation
- contract tests for auth guidance, payload-boundary wording, and review-surface completeness
- transport tests confirming report requests preserve the declared endpoint identity, supported body shape, OAuth access, and 204-success acknowledgement behavior

## Invariants

- This contract remains internal to Layer 1 and does not create a public MCP tool
- The wrapper must keep quota cost `50` visible alongside auth and payload-boundary guidance
- New or changed Python functions involved in auth or body validation must include reStructuredText docstrings
- The feature must preserve the existing shared executor, auth-context plumbing, retry behavior, and observability hooks outside the intentional endpoint addition
