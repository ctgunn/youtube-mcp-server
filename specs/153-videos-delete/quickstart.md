# Quickstart: YT-153 Layer 1 Endpoint `videos.delete`

## Purpose

Use this feature to add a reviewable internal `videos.delete` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, OAuth-only expectations, deterministic target identifier validation, no-body delete guidance, and normalized acknowledgement outcomes suitable for downstream reuse.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server` on branch `153-videos-delete`
- Keep the slice internal to Layer 1; do not add a public MCP `videos_delete` tool in this feature
- Preserve the existing Layer 1 executor, auth context, retry, observability, and normalized error patterns
- Add or preserve reStructuredText docstrings for every new or changed Python function

## Red Phase

1. Add failing unit tests for `videos.delete` metadata completeness, quota visibility, required `id` validation, no-body behavior, 204-success acknowledgement guidance, and OAuth-only enforcement.
2. Add failing transport tests for authorized `DELETE /youtube/v3/videos` request construction, required `id` query parameter handling, bearer authorization header use, no request-body transmission, and 204 no-content acknowledgement normalization.
3. Add failing integration tests showing the wrapper executes through the shared executor for valid authorized requests and rejects invalid request shapes before execution.
4. Add failing contract tests showing feature-local contracts, wrapper metadata, and consumer summaries do not yet make the delete boundary reviewable enough for downstream reuse.

## Green Phase

1. Add a typed `videos.delete` Layer 1 wrapper using the existing endpoint metadata and representative wrapper patterns.
2. Record endpoint identity as resource `videos`, method `delete`, operation key `videos.delete`, method `DELETE`, path `/youtube/v3/videos`, quota cost `50`, and auth mode `oauth_required`.
3. Validate the required `id` target identifier before execution.
4. Reject or clearly flag request bodies and unsupported request modifiers.
5. Preserve or clearly document partner-only `onBehalfOfContentOwner` behavior according to the final wrapper boundary.
6. Normalize successful no-content upstream responses into deletion acknowledgement results that preserve the target video id and source contract details.
7. Keep OAuth tokens, credentials, target-owner identity, and delegated-owner credentials out of results, logs, docs, and tests.

## Refactor Phase

1. Align naming, request validation, acknowledgement result shaping, and consumer-summary fields with neighboring delete and video wrappers.
2. Remove duplicated quota, auth, and delete-boundary wording where shared metadata or contract text already carries it clearly.
3. Confirm the feature remains a single-endpoint internal Layer 1 slice with no public MCP tool, no hosted runtime change, and no broader video lifecycle workflow.
4. Run targeted Layer 1 tests first, then complete full repository verification.

## Suggested Verification Commands

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_videos_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
python3 -m ruff check .
```

## Review Checklist

- `videos.delete` wrapper metadata shows endpoint identity and quota cost `50`
- OAuth-required access is visible in metadata, contracts, docstrings, and tests
- Required `id` target-video input is visible and validated
- Request body behavior is explicitly rejected or clearly flagged
- Partner-only `onBehalfOfContentOwner` behavior is explicitly supported or explicitly outside the guaranteed slice boundary
- Successful 204 no-content responses are normalized into deletion acknowledgements
- Validation, access, forbidden, not-found, upstream-unavailable, and success outcomes remain distinct
- No public MCP tool is introduced by this slice
- New or changed Python functions have reStructuredText docstrings
- Final evidence includes `python3 -m pytest` and `python3 -m ruff check .`
