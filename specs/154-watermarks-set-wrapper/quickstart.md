# Quickstart: YT-154 Layer 1 Endpoint `watermarks.set`

## Purpose

Use this feature to add a reviewable internal `watermarks.set` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, OAuth-only expectations, deterministic target-channel validation, watermark resource metadata guidance, media-upload constraints, and normalized acknowledgement outcomes suitable for downstream reuse.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server` on branch `154-watermarks-set-wrapper`
- Keep the slice internal to Layer 1; do not add a public MCP `watermarks_set` tool in this feature
- Preserve the existing Layer 1 executor, auth context, retry, observability, media upload, and normalized error patterns
- Add or preserve reStructuredText docstrings for every new or changed Python function

## Red Phase

1. Add failing unit tests for `watermarks.set` metadata completeness, quota visibility, required `channelId` validation, required watermark resource metadata, required `media` payload, supported media boundaries, `204 No Content` acknowledgement guidance, and OAuth-only enforcement.
2. Add failing transport tests for authorized `POST /upload/youtube/v3/watermarks/set` request construction, required `channelId` query parameter handling, bearer authorization header use, watermark resource and media upload handling, and 204 no-content acknowledgement normalization.
3. Add failing integration tests showing the wrapper executes through the shared executor for valid authorized requests and rejects invalid request shapes before execution when determinable locally.
4. Add failing contract tests showing feature-local contracts, wrapper metadata, and consumer summaries do not yet make the watermark upload boundary reviewable enough for downstream reuse.

## Green Phase

1. Add a typed `watermarks.set` Layer 1 wrapper using the existing endpoint metadata and representative wrapper patterns.
2. Record endpoint identity as resource `watermarks`, method `set`, operation key `watermarks.set`, method `POST`, path `/upload/youtube/v3/watermarks/set`, quota cost `50`, and auth mode `oauth_required`.
3. Validate the required `channelId` target channel before execution.
4. Validate the required watermark resource metadata before execution.
5. Validate the required `media` upload payload, including supported MIME type and maximum-size boundaries where determinable locally.
6. Reject or clearly flag unsupported request modifiers.
7. Preserve or clearly document partner-only `onBehalfOfContentOwner` behavior according to the final wrapper boundary.
8. Normalize successful no-content upstream responses into watermark-update acknowledgement results that preserve target channel id and source contract details.
9. Keep OAuth tokens, credentials, channel-owner identity, delegated-owner credentials, and raw media bytes out of results, logs, docs, and tests.

## Refactor Phase

1. Align naming, request validation, acknowledgement result shaping, and consumer-summary fields with neighboring upload and mutation wrappers.
2. Remove duplicated quota, auth, watermark, and upload-boundary wording where shared metadata or contract text already carries it clearly.
3. Confirm the feature remains a single-endpoint internal Layer 1 slice with no public MCP tool, no hosted runtime change, and no broader channel-branding workflow.
4. Run targeted Layer 1 tests first, then complete full repository verification.

## Suggested Verification Commands

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
python3 -m ruff check .
```

## Review Checklist

- `watermarks.set` wrapper metadata shows endpoint identity and quota cost `50`
- OAuth-required access is visible in metadata, contracts, docstrings, and tests
- Required `channelId` target-channel input is visible and validated
- Required watermark resource metadata is visible and validated
- Required `media` upload payload is visible and validated
- Media MIME type and maximum-size boundaries are documented and tested
- Partner-only `onBehalfOfContentOwner` behavior is explicitly supported or explicitly outside the guaranteed slice boundary
- Successful 204 no-content responses are normalized into watermark-update acknowledgements
- Validation, access, unsupported-media, forbidden-channel, upstream-unavailable, and success outcomes remain distinct
- No public MCP tool is introduced by this slice
- New or changed Python functions have reStructuredText docstrings
- Final evidence includes `python3 -m pytest` and `python3 -m ruff check .`
