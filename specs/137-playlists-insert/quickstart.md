# Quickstart: YT-137 Layer 1 Endpoint `playlists.insert`

## Goal

Use this feature to add a reviewable internal `playlists.insert` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit writable `snippet` guidance, visible OAuth-only expectations, deterministic rejection of unsupported request combinations, and normalized creation outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/contracts/layer1-playlists-insert-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/contracts/layer1-playlists-insert-wrapper-contract.md)
- Read the auth and write-boundary contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/contracts/layer1-playlists-insert-auth-write-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/contracts/layer1-playlists-insert-auth-write-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `playlists.insert` metadata completeness, quota visibility, writable-input validation, and OAuth-only enforcement.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unauthorized, and upstream-rejected playlist-creation profiles.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `playlists.insert` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, OAuth-only access, required create inputs, and unsupported writable-boundary rules visible without exposing credentials, including summary fields for required request fields, the active writable part, and the nested required title field.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, missing OAuth access distinct from malformed input, and authorized upstream rejections distinct from successful creation outcomes.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlists_contract.py`

## 3. Keep scope constrained

- Keep YT-137 internal-only.
- Do not add a public `playlists_insert` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on writable-input boundaries, quota visibility, OAuth expectations, and normalized creation outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_playlists_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `playlists.insert` wrapper metadata shows endpoint identity and the quota cost of `50`
- Required writable `snippet` inputs are clear
- Higher-layer playlist-create summaries show required fields, the active writable part, and the required nested title field
- OAuth-only access is visible without reading implementation code
- Unsupported request combinations are explicit in wrapper and contract surfaces
- Missing playlist title input fails clearly
- Authorized upstream create failures remain distinct from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
