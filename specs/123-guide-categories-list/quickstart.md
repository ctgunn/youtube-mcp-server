# Quickstart: YT-123 Layer 1 Endpoint `guideCategories.list`

## Goal

Add a reviewable internal `guideCategories.list` wrapper on top of the existing Layer 1 foundation with explicit `part` plus `regionCode` rules, API-key visibility, deprecated-or-unavailable lifecycle guidance, quota visibility, and normalized retrieval outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-wrapper-contract.md)
- Read the region-lifecycle contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-region-lifecycle-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-region-lifecycle-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `guideCategories.list` metadata completeness, quota visibility, lifecycle-state visibility, and required `part` plus `regionCode` validation.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, lifecycle-aware unavailable, and empty-result guide-category profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make request boundaries, API-key behavior, and deprecated lifecycle guidance reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, API-key access expectations, `part` plus `regionCode` rules, and lifecycle caveat guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, deprecated-or-unavailable endpoint failures on `lifecycle_unavailable`, and valid zero-item results on the success path.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_legacy_categories_contract.py`

## 3. Keep scope constrained

- Keep YT-123 internal-only.
- Do not add a public `guideCategories_list` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on request boundaries, quota visibility, lifecycle caveat handling, API-key expectations, and normalized retrieval outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_legacy_categories_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `guideCategories.list` wrapper metadata shows endpoint identity and quota cost `1`
- Supported request inputs and deterministic validation rules are clear
- API-key access expectations are visible without reading implementation code
- Deprecated-or-unavailable lifecycle guidance is visible in wrapper and higher-layer review surfaces
- Missing `part` or `regionCode` inputs fail clearly
- Lifecycle-aware unavailable outcomes are distinct from invalid requests
- Empty result sets for valid requests remain success outcomes
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
