# Quickstart: YT-141 Layer 1 Endpoint `subscriptions.list`

## Goal

Add a reviewable internal `subscriptions.list` wrapper on top of the existing Layer 1 foundation with explicit required `part` rules, exactly-one-selector validation, selector-aware OAuth guidance, collection-specific paging and ordering rules, quota visibility, unsupported-combination guidance, and normalized retrieval outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-wrapper-contract.md)
- Read the filter-modes contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-filter-modes-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-filter-modes-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `subscriptions.list` metadata completeness, quota visibility, required `part` validation, exactly-one-selector enforcement, selector-aware auth validation, and collection-specific paging and ordering validation.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, access-denied, and empty-result subscription profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make selector boundaries, OAuth expectations, paging and ordering behavior, and unsupported-combination guidance reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, selector-aware auth behavior, collection-versus-direct lookup behavior, paging and ordering guidance, and unsupported-combination boundaries visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, incompatible auth usage distinct from malformed input, and valid zero-item results on the success path.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` when selector-aware higher-layer summaries are updated in scope

## 3. Keep scope constrained

- Keep YT-141 internal-only.
- Do not add a public `subscriptions_list` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on selector boundaries, selector-aware OAuth rules, paging and ordering behavior, quota visibility, unsupported combinations, and normalized retrieval outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_subscriptions_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `subscriptions.list` wrapper metadata shows endpoint identity and quota cost `1`
- Supported selector inputs and collection-versus-direct lookup rules are clear
- Public-compatible versus OAuth-backed selector expectations are visible without reading implementation code
- Unsupported paging and ordering combinations are explicit in wrapper and contract surfaces
- Missing `part` or conflicting selectors fail clearly
- Valid empty result sets remain success outcomes
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
