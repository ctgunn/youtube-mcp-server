# Quickstart: YT-144 Layer 1 Endpoint `thumbnails.set`

## Goal

Use this feature to add a reviewable internal `thumbnails.set` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit `videoId` plus `media` guidance, visible OAuth-only expectations, deterministic rejection of unsupported request combinations, and normalized thumbnail-update outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-wrapper-contract.md)
- Read the auth and upload contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-auth-upload-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-auth-upload-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `thumbnails.set` metadata completeness, quota visibility, `videoId`-plus-upload validation, and OAuth-only enforcement.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unauthorized, target-video-rejected, and upstream-rejected thumbnail-update profiles.
3. Add failing integration and contract tests showing the representative wrapper path does not yet make `thumbnails.set` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, OAuth-only access, required update inputs, and target-video and invalid-request boundaries visible without exposing credentials or raw media content.
6. Refactor for naming clarity and duplication reduction while preserving deterministic request validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.
8. Confirm failure-path behavior keeps malformed requests on `invalid_request`, missing OAuth access on `auth`, target-video restrictions on `target_video`, and authorized upstream rejections on `upstream_service`, all distinct from successful update outcomes.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_thumbnails_contract.py`

## 3. Keep scope constrained

- Keep YT-144 internal-only.
- Do not add a public `thumbnails_set` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on update-input boundaries, upload guidance, quota visibility, OAuth expectations, target-video failures, and normalized thumbnail-update outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_thumbnails_contract.py
python3 -m pytest
python3 -m ruff check .
```

## 5. Review readiness checklist

- `thumbnails.set` wrapper metadata shows endpoint identity and the quota cost of `50`
- Required `videoId` plus `media` inputs are clear
- OAuth-only access is visible without reading implementation code
- Unsupported request combinations are explicit in wrapper and contract surfaces
- Missing `videoId` or missing upload input fail clearly
- Target-video restrictions remain distinct from local validation failures
- Authorized upstream update failures remain distinct from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
