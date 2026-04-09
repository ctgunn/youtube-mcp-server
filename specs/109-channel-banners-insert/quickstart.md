# Quickstart: YT-109 Layer 1 Endpoint `channelBanners.insert`

## Goal

Use this feature to add a reviewable internal `channelBanners.insert` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit image-upload guidance, visible OAuth and delegation notes, deterministic upload validation, and a stable result that preserves the returned banner URL for later channel-branding work.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/plan.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-wrapper-contract.md)
- Read the auth-upload contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-auth-upload-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-auth-upload-contract.md)

## 2. Implement the feature in Red-Green-Refactor order

1. Add failing unit tests for `channelBanners.insert` metadata completeness, quota visibility, required media input, optional delegation handling, OAuth-only enforcement, and response-URL reviewability.
2. Add failing contract tests for maintainer-facing artifacts that must explain image constraints, optional delegation guidance, response-URL handoff behavior, and the supported boundary for banner uploads.
3. Add failing integration and transport tests showing the representative wrapper path does not yet make `channelBanners.insert` reusable for channel-branding planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and any narrowly necessary supporting integration modules needed to satisfy those failures.
5. Ensure the wrapper review surface exposes endpoint identity, `quotaCost`, OAuth-required guidance, the supported `media` upload boundary, image constraints, and `onBehalfOfContentOwner` guidance clearly enough for later channel-branding work.
6. Update higher-layer review flows so consumer-facing summaries can expose `channelBanners.insert` source operation, quota, auth mode, upload constraints, returned banner URL, and the stable `access-denied` versus `invalid-upload` versus `target-channel` failure boundary without leaking raw upstream details or binary media content.
7. Refactor for naming clarity, reduced duplication, and complete reStructuredText docstrings on all new or changed Python functions.

Representative implementation modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_banners_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

## 3. Keep the change scoped

- Keep YT-109 internal-only.
- Do not add a public `channelBanners_insert` MCP tool here; that belongs to later Layer 2 work.
- Reuse the YT-101 executor and YT-102 metadata standards instead of inventing a second endpoint-wrapper abstraction.
- Focus on media validation, upload visibility, auth visibility, delegation visibility, quota visibility, response-URL handling, and normalized banner-upload outcomes rather than broader channel-branding feature expansion.

## 4. Verify before review

Run the targeted and full validation steps expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest tests/contract/test_layer1_channel_banners_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `channelBanners.insert` wrapper metadata shows endpoint identity and the quota cost of `50`
- Maintainer-facing artifacts state that authorized access is required
- Supported request inputs identify one banner-image upload payload and the documented optional `onBehalfOfContentOwner` delegation input
- Image constraints are visible before reuse
- A successful upload remains reviewable through a normalized result that preserves the returned banner URL
- Unsupported or incomplete upload requests are rejected or clearly flagged before execution
- `auth`, `invalid_request`, and `target_channel` failure outcomes remain distinguishable for higher-layer reuse
- Higher-layer review surfaces preserve quota, auth, upload, and response-URL guidance
- No public MCP tool or hosted behavior changes are introduced in this slice
- Existing Layer 1 execution behavior remains intact outside the endpoint-specific additions
- All new or changed Python functions include reStructuredText docstrings
