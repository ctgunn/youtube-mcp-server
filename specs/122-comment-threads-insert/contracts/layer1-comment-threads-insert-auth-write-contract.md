# Contract: YT-122 Layer 1 `commentThreads.insert` Auth and Write Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `commentThreads.insert` authorization requirements, top-level-thread-create rules, delegation guidance, target-eligibility handling, and invalid-create boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible top-level-thread-create guidance for the supported write path
- clear rejection of unsupported reply-style or mixed comment-thread create shapes
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and create-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a comment-thread create path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported create shapes are supplied

## Authorization Rules

Required behavior:

- `commentThreads.insert` requires authorized comment-thread write access
- auth mismatch failures must remain explicit rather than blending into invalid create-shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- optional write-context or delegation guidance must remain visible for eligible authorized requests
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Top-Level Thread-Create Rules

The wrapper contract for this slice must document:

- that the supported create boundary is top-level thread creation
- that the request body must identify the supported video target
- that the request body must include non-empty top-level comment content
- that unsupported reply-style or mixed comment-thread create shapes fall outside the wrapper boundary
- that the supported top-level path is intended for direct later Layer 2 and Layer 3 reuse

For supported create paths, the contract must explain:

- that `body.snippet.videoId` and `body.snippet.topLevelComment.snippet.textOriginal` activate the supported top-level-thread boundary
- what top-level comment content is expected
- what authorization behavior is required before the create may proceed
- whether optional delegation inputs are preserved in successful normalized results

## Invalid-Create Handling

The contract must treat create-shape validation as deterministic.

Required behavior:

- callers may not omit `part`, `body`, the supported discussion target, or top-level comment content and still expect supported wrapper behavior
- callers may not supply unsupported create fields or conflicting create fields and still expect supported wrapper behavior
- callers may not rely on reply-style comment creation through this slice
- contract and test artifacts must keep these boundaries reviewable

## Target Eligibility Guidance

The contract must explain that:

- some validly shaped authorized create requests can still fail because the targeted discussion context is unavailable, comments-disabled, or otherwise inaccessible or ineligible in the current authorization context
- higher-layer callers should treat those outcomes as target-eligibility failures rather than local contract ambiguity
- successful created-thread handling remains separate from target-eligibility failures, upstream rejections, and local validation failures

## Validation Expectations

Representative proof for YT-122 must show:

- maintainers can identify OAuth-required behavior in one review pass
- top-level-thread-create rules are documented clearly enough for future comment-thread features
- unsupported reply-style or mixed create shapes are protected by regression coverage
- target-eligibility handling remains distinct from malformed requests and auth failures
- created-thread handling remains on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/`
- unit coverage for create-shape validation and auth enforcement
- transport coverage showing `POST` request construction for `commentThreads.insert`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
