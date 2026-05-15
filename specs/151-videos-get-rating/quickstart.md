# Quickstart: YT-151 Layer 1 Endpoint `videos.getRating`

## Goal

Use this feature to add a reviewable internal `videos.getRating` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, visible OAuth-only expectations, deterministic identifier validation, explicit returned rating-state guidance, and normalized lookup outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-wrapper-contract.md)
- Read the auth and rating-state contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-auth-rating-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-auth-rating-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `videos.getRating` metadata completeness, quota visibility, identifier validation, returned rating-state guidance, and OAuth-only enforcement.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unauthorized, upstream-failing, rated, and unrated video-rating lookup profiles.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `videos.getRating` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, OAuth-only access, required identifier input, and returned rating-state rules visible without exposing credentials, including summary fields for the request identifier boundary, returned rating count, unrated-item presence, and source contract details.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, missing OAuth access distinct from malformed input, upstream lookup failures distinct from successful lookup outcomes, and successful unrated results distinct from failures.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

## 3. Keep scope constrained

- Keep YT-151 internal-only.
- Do not add a public `videos_getRating` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on identifier-boundary validation, quota visibility, OAuth expectations, returned rating-state semantics, and normalized lookup outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_videos_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `videos.getRating` wrapper metadata shows endpoint identity and the quota cost of `1`
- Required identifier input is clear
- The supported `id` boundary is reviewable as one comma-delimited field with at most 50 video identifiers
- Higher-layer rating-lookup summaries show the request identifier boundary, returned rating count, unrated-item presence, and source contract details
- OAuth-only access is visible without reading implementation code
- Supported returned rating states are explicit in wrapper and contract surfaces
- Unsupported request combinations are explicit in wrapper and contract surfaces
- Missing identifier input fails clearly
- Authorized upstream lookup failures remain distinct from local validation failures and successful unrated results
- Temporary upstream lookup outages remain distinguishable as `upstream_unavailable`
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
