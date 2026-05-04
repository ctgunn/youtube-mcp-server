# Quickstart: YT-140 Layer 1 Endpoint `search.list`

## Goal

Add a reviewable internal `search.list` wrapper on top of the existing Layer 1 foundation with explicit required search inputs, visible high-quota and quota-caveat guidance, conditional-auth visibility, deterministic refinement validation, and normalized populated-result, empty-result, and failure outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-wrapper-contract.md)
- Read the auth-refinement contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-auth-refinement-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-auth-refinement-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `search.list` metadata completeness, quota visibility, quota caveat visibility, required `part` and `q` validation, conditional-auth enforcement, and unsupported-field rejection.
2. Add failing transport tests for request construction and normalized result handling for populated results, empty results, incompatible search refinements, and restricted-auth request paths.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `search.list` reusable for higher-layer planning and does not yet separate `invalid_request`, auth, and upstream-service failures clearly enough.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures, including the internal higher-layer review path for search behavior.
5. Ensure review surfaces keep operation identity, quota cost, quota caveat, required search inputs, search refinements, and authorization expectations visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic refinement validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_search_contract.py`

## 3. Keep scope constrained

- Keep YT-140 internal-only.
- Do not add a public `search_list` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on required search inputs, quota visibility, quota caveat visibility, conditional-auth behavior, supported search refinements, and normalized search outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest tests/contract/test_layer1_search_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `search.list` wrapper metadata shows endpoint identity and quota cost `100`
- Search quota caveat is explicit and reviewable
- Conditional-auth behavior is explicit and public-only baseline search is not confused with restricted-filter search
- Missing required search inputs and malformed requests fail clearly
- Unsupported refinement combinations fail clearly
- Upstream `400` search failures remain distinguishable as `invalid_request`
- Restricted-auth denials remain distinguishable from local invalid-request failures
- Empty-result search outcomes remain distinguishable from local validation failures and upstream search failures
- Normalized upstream search failures remain distinguishable from local validation failures
- Search results keep enough request context visible for downstream interpretation
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
