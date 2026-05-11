# Contract: YT-148 Layer 1 `videos.insert` Auth and Upload Contract

## Purpose

Define the maintainer-facing rules for OAuth-only access, supported upload modes, and audit/private-default caveats for the internal `videos.insert` wrapper.

## Authorization Rules

- `videos.insert` is OAuth-only for every supported request path in this slice.
- Missing or incompatible OAuth access must remain distinguishable from invalid request shapes.
- Auth expectations must stay visible in wrapper metadata, docstrings, and higher-layer summaries.
- Credential material must never be surfaced in docs, tests, logs, or review artifacts.

## Upload Rules

- A supported request includes `part`, `body`, and `media`.
- Metadata-only requests are invalid.
- Upload-only requests are invalid.
- Upload guidance must explicitly name the supported mode or modes instead of requiring maintainers to infer behavior from transport code.
- Resumable-upload support, when available for this slice, must explain the caller-visible follow-up expectation clearly enough that higher-layer authors can decide whether the mode fits their workflow.
- Unsupported upload-mode combinations or undocumented upload hints must fail as `invalid_request` or an equivalent normalized validation outcome before execution.

## Quota and Reviewability Rules

- The official quota cost (`1600`) must remain highly visible in metadata, docstrings, and contract artifacts because `videos.insert` is one of the most expensive upstream methods in the repository.
- Higher-layer summaries must preserve source operation, auth mode, quota cost, and caveat visibility so downstream planning does not require rereading the wrapper implementation.

## Audit and Private-Default Caveat Rules

- The wrapper must keep a reviewable note explaining that upload success does not remove the audit/private-default caveat.
- The review surface must make it clear why the caveat matters for reuse, especially when a maintainer is interpreting initial video visibility or release-readiness after creation.
- The audit/private-default caveat must remain separate from invalid request handling and unauthorized access handling.
- A successful create result may still carry caveat implications that later video-publishing workflows must account for.

## Failure-Boundary Rules

- `invalid_request` remains the boundary for missing metadata, missing upload content, unsupported fields, or unsupported upload-mode combinations.
- Unauthorized access remains a separate boundary for requests that do not satisfy the OAuth-only requirement.
- Policy-caveat interpretation remains separate from invalid input: the audit/private-default caveat affects reuse expectations and result interpretation, not whether the wrapper contract itself was valid.
- Normalized upstream create failures remain distinct from all of the above so higher layers can tell the difference between request-shape issues, access issues, caveat-sensitive success, and upstream refusal.

## Review Validation Expectations

The feature should make it possible for a maintainer to verify from repository artifacts alone that:

- `videos.insert` is OAuth-only
- `body` and `media` are both required
- supported upload modes are documented with clear caller-facing expectations
- quota cost `1600` is easy to find
- the audit/private-default caveat remains visible in the review surface
- invalid requests remain separate from unauthorized access and from caveat-sensitive success
