# Quickstart: YT-131 Layer 1 Endpoint `playlistImages.delete`

## Goal

Add a reviewable internal `playlistImages.delete` wrapper on top of the existing Layer 1 foundation with explicit target-playlist-image rules, OAuth-required visibility, deterministic delete-target validation, quota visibility, and normalized deletion-acknowledgment outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/contracts/layer1-playlist-images-delete-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/contracts/layer1-playlist-images-delete-wrapper-contract.md)
- Read the auth-delete contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/contracts/layer1-playlist-images-delete-auth-delete-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/contracts/layer1-playlist-images-delete-auth-delete-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `playlistImages.delete` metadata completeness, quota visibility, OAuth enforcement, required target identifier validation, and unsupported-field rejection.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unavailable-target, and upstream-rejected delete profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make delete preconditions, authorization expectations, and normalized upstream failures reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures, including the internal higher-layer review path for playlist-image deletion.
5. Ensure review surfaces keep operation identity, quota cost, delete preconditions, authorization expectations, and unavailable-target guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic delete validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py`

## 3. Keep scope constrained

- Keep YT-131 internal-only.
- Do not add a public `playlistImages_delete` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on delete-target rules, quota visibility, OAuth-required behavior, and normalized deletion outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_playlist_images_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `playlistImages.delete` wrapper metadata shows endpoint identity and quota cost `50`
- Delete preconditions are clear
- OAuth-required behavior is explicit and public-only delete access is not implied
- Missing authorization and malformed delete requests fail clearly
- Unavailable delete targets remain distinguishable from local validation failures
- Normalized upstream delete failures remain distinguishable from local validation failures
- Deletion acknowledgment keeps the targeted playlist-image identity visible
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
