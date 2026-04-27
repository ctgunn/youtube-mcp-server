# Quickstart: YT-130 Layer 1 Endpoint `playlistImages.update`

## Goal

Use this feature to add a reviewable internal `playlistImages.update` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit identifying `body` plus `media` guidance, visible OAuth-only expectations, deterministic rejection of unsupported request combinations, and normalized update outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-wrapper-contract.md)
- Read the auth and media contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-auth-media-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-auth-media-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `playlistImages.update` metadata completeness, quota visibility, identifying-body-plus-media validation, and OAuth-only enforcement.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unauthorized, and upstream-rejected playlist-image update profiles.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `playlistImages.update` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, OAuth-only access, required update inputs, and invalid-request boundaries visible without exposing credentials or raw media content.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, missing OAuth access distinct from malformed input, and authorized upstream update failures distinct from successful update outcomes.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py`

## 3. Keep scope constrained

- Keep YT-130 internal-only.
- Do not add a public `playlistImages_update` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on update-input boundaries, media guidance, quota visibility, OAuth expectations, and normalized update outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_playlist_images_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `playlistImages.update` wrapper metadata shows endpoint identity and the quota cost of `50`
- Required identifying `body` plus `media` inputs are clear
- OAuth-only access is visible without reading implementation code
- Unsupported request combinations are explicit in wrapper and contract surfaces
- Missing identifiers, missing metadata, or missing media input fail clearly
- Authorized upstream update failures remain distinct from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
