# Quickstart: YT-155 Layer 1 Endpoint `watermarks.unset`

## Purpose

Use this feature to add a reviewable internal `watermarks.unset` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, OAuth-only expectations, deterministic target-channel validation, no-upload request guidance, no-removal-possible handling, and normalized acknowledgement outcomes suitable for downstream reuse.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server` on branch `155-watermarks-unset-wrapper`
- Keep the slice internal to Layer 1; do not add a public MCP `watermarks_unset` tool in this feature
- Preserve the existing Layer 1 executor, auth context, retry, observability, upload, and normalized error patterns
- Add or preserve reStructuredText docstrings for every new or changed Python function

## Red Phase

1. Add failing unit tests for `watermarks.unset` metadata completeness, quota visibility, required `channelId` validation, no-upload request boundary, no-content acknowledgement guidance, no-removal-possible guidance, and OAuth-only enforcement.
2. Add failing transport tests for authorized `POST /youtube/v3/watermarks/unset` request construction, required `channelId` query parameter handling, bearer authorization header use, absence of body/media upload handling, and 204 no-content acknowledgement normalization.
3. Add failing integration tests showing the wrapper executes through the shared executor for valid authorized requests and rejects invalid request shapes before execution when determinable locally.
4. Add failing contract tests showing feature-local contracts, wrapper metadata, and consumer summaries do not yet make the watermark removal boundary reviewable enough for downstream reuse.

## Green Phase

1. Add a typed `watermarks.unset` Layer 1 wrapper using the existing endpoint metadata and representative wrapper patterns.
2. Record endpoint identity as resource `watermarks`, method `unset`, operation key `watermarks.unset`, method `POST`, path `/youtube/v3/watermarks/unset`, quota cost `50`, and auth mode `oauth_required`.
3. Validate the required `channelId` target channel before execution.
4. Reject or clearly flag `body`, `media`, watermark metadata, upload payloads, and unsupported request modifiers.
5. Preserve or clearly document partner-only `onBehalfOfContentOwner` behavior according to the final wrapper boundary.
6. Normalize successful no-content upstream responses into watermark-removal acknowledgement results that preserve target channel id and source contract details.
7. Normalize no-current-watermark or already-removed outcomes distinctly from successful removal, invalid request, forbidden channel, and upstream-unavailable outcomes.
8. Keep OAuth tokens, credentials, channel-owner identity, delegated-owner credentials, and unrelated media data out of results, logs, docs, and tests.

## Refactor Phase

1. Align naming, request validation, acknowledgement result shaping, and consumer-summary fields with neighboring mutation wrappers.
2. Remove duplicated quota, auth, channel, and no-upload boundary wording where shared metadata or contract text already carries it clearly.
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

- `watermarks.unset` wrapper metadata shows endpoint identity and quota cost `50`
- OAuth-required access is visible in metadata, contracts, docstrings, and tests
- Required `channelId` target-channel input is visible and validated
- `body`, `media`, watermark metadata, and upload payloads are explicitly outside the unset boundary
- Partner-only `onBehalfOfContentOwner` behavior is explicitly supported or explicitly outside the guaranteed slice boundary
- Successful 204 no-content responses are normalized into watermark-removal acknowledgements
- No-current-watermark and already-removed outcomes remain distinct from successful removals
- Validation, access, unsupported-payload, forbidden-channel, no-removal, upstream-unavailable, and success outcomes remain distinct
- No public MCP tool is introduced by this slice
- New or changed Python functions have reStructuredText docstrings
- Final evidence includes `python3 -m pytest` and `python3 -m ruff check .`
