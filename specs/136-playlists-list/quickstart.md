# Quickstart: YT-136 Layer 1 Endpoint `playlists.list`

## Goal

Add a reviewable internal `playlists.list` wrapper on top of the existing Layer 1 foundation with explicit required `part` rules, exactly-one-selector validation, selector-aware auth guidance, filter-specific paging rules, quota visibility, unsupported modifier guidance, and normalized retrieval outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-wrapper-contract.md)
- Read the filter-modes contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-filter-modes-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-filter-modes-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `playlists.list` metadata completeness, quota visibility, required `part` validation, exactly-one-selector enforcement, selector-aware auth validation, and filter-specific paging validation.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, access-denied, and empty-result playlist profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make filter boundaries, auth expectations, paging behavior, and unsupported modifier guidance reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, selector-aware auth behavior, filter rules, paging guidance, and unsupported modifier boundaries visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, incompatible auth usage distinct from malformed input, and valid zero-item results on the success path.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

## 3. Keep scope constrained

- Keep YT-136 internal-only.
- Do not add a public `playlists_list` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on filter boundaries, selector-aware auth rules, paging behavior, quota visibility, unsupported modifiers, and normalized retrieval outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_channels_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `playlists.list` wrapper metadata shows endpoint identity and quota cost `1`
- Supported selector inputs and paging rules are clear
- Public versus owner-scoped auth expectations are visible without reading implementation code
- Unsupported modifiers are explicit in wrapper and contract surfaces
- Missing `part` or conflicting selectors fail clearly
- Valid empty result sets remain success outcomes
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
