# Quickstart: YT-150 Layer 1 Endpoint `videos.rate`

## Goal

Use this feature to add a reviewable internal `videos.rate` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit `like`/`dislike`/`none` guidance, visible OAuth-only expectations, deterministic rejection of unsupported request combinations, and normalized acknowledgement outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-wrapper-contract.md)
- Read the auth and rating-boundary contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-auth-rating-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-auth-rating-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `videos.rate` metadata completeness, quota visibility, identifier enforcement, supported rating-action validation, and OAuth-only enforcement.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unauthorized, and upstream-rejected video-rating profiles.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `videos.rate` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, OAuth-only access, required request inputs, and supported rating semantics visible without exposing credentials, including summary fields for required request fields, the target identifier field, and the requested rating action.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm the higher-layer `rate_video_summary()` path preserves `videoId`, `requestedRating`, `ratingState`, quota visibility, and required-field guidance for maintainers.
9. Confirm failure-path behavior keeps malformed requests on `invalid_request`, missing OAuth access distinct from malformed input, and authorized upstream rating failures such as `not_found` or `policy_restricted` distinct from successful acknowledgement outcomes.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

## 3. Keep scope constrained

- Keep YT-150 internal-only.
- Do not add a public `videos_rate` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on `id` plus `rating` boundaries, quota visibility, OAuth expectations, and normalized acknowledgement outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_videos_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `videos.rate` wrapper metadata shows endpoint identity and the quota cost of `50`
- Supported `like`, `dislike`, and `none` semantics are clear
- Higher-layer video-rating summaries show required fields, the target identifier field, and the requested rating action
- Higher-layer video-rating summaries preserve `ratingState` and whether the path cleared or applied a rating
- OAuth-only access is visible without reading implementation code
- Unsupported request combinations are explicit in wrapper and contract surfaces
- Missing target identifier or unsupported rating input fails clearly
- Authorized upstream rating failures remain distinct from local validation failures and missing OAuth access
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
