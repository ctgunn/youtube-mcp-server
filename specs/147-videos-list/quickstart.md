# Quickstart: YT-147 Layer 1 Endpoint `videos.list`

## Goal

Add a reviewable internal `videos.list` wrapper on top of the existing Layer 1 foundation with explicit selector rules, mixed-auth visibility, collection-refinement boundaries, quota visibility, and normalized retrieval outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-wrapper-contract.md)
- Read the selector and auth contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-selector-auth-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/layer1-videos-list-selector-auth-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `videos.list` metadata completeness, quota visibility, selector exclusivity, mixed-auth review surfaces, and supported collection-refinement validation boundaries.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, and empty-result video retrieval profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make selector rules, mixed-auth behavior, and chart-refinement guidance reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, mixed-auth expectations, selector rules, and supported optional refinements visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request` and valid zero-item results on the success path.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

## 3. Keep scope constrained

- Keep YT-147 internal-only.
- Do not add a public `videos_list` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on selector boundaries, mixed-auth visibility, chart-refinement guidance, quota visibility, and normalized retrieval outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_videos_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `videos.list` wrapper metadata shows endpoint identity and quota cost `1`
- Supported selector inputs and exclusivity rules are clear
- Mixed-auth expectations are visible without reading implementation code
- Chart-oriented refinements and paging boundaries are visible in wrapper and higher-layer review surfaces
- Missing `part` or selector inputs fail clearly
- Conflicting selectors fail clearly
- Unsupported chart-only refinements fail clearly outside chart retrieval
- Empty result sets for valid requests remain success outcomes
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
