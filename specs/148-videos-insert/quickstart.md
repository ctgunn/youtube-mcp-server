# Quickstart: YT-148 Layer 1 Endpoint `videos.insert`

## Goal

Use this feature to add a reviewable internal `videos.insert` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit `body` plus `media` guidance, visible OAuth-only behavior, documented upload-mode expectations, and a reviewable audit/private-default caveat.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/plan.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-wrapper-contract.md)
- Read the auth and upload contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-auth-upload-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-auth-upload-contract.md)

## 2. Implement the feature in Red-Green-Refactor order

1. Add failing unit tests for `videos.insert` metadata completeness, quota visibility, metadata-plus-upload validation, upload-mode guidance, lifecycle caveat visibility, and OAuth-only enforcement.
2. Add failing contract tests for maintainer-facing artifacts that must explain upload sensitivity, supported upload modes, and the audit/private-default caveat.
3. Add failing integration and transport tests showing the representative wrapper path does not yet make `videos.insert` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and any narrowly necessary supporting integration modules needed to satisfy those failures.
5. Ensure the wrapper review surface exposes endpoint identity, `quotaCost`, OAuth-required guidance, supported upload modes, and the audit/private-default caveat clearly enough for later video-publishing work.
6. Update higher-layer review flows so consumer-facing summaries can expose `videos.insert` source operation, quota, auth mode, and caveat visibility without leaking raw upstream details or upload content.
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
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

## 3. Keep the change scoped

- Keep YT-148 internal-only.
- Do not add a public `videos_insert` MCP tool here; that belongs to later Layer 2 work.
- Reuse the YT-101 executor and YT-102 metadata standards instead of inventing a second endpoint-wrapper abstraction.
- Focus on metadata-plus-upload validation, upload-mode guidance, auth visibility, quota visibility, caveat visibility, and created-resource handling rather than broader video-publishing expansion.

## 4. Verify before review

Run the targeted and full validation steps expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_videos_contract.py
python3 -m pytest tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `videos.insert` wrapper metadata shows endpoint identity and the quota cost of `1600`
- Maintainer-facing artifacts state that authorized access is required
- Supported request inputs distinguish the required `body` metadata payload from the required `media` upload payload
- Supported upload modes are visible before reuse
- The audit/private-default caveat is visible before reuse and remains distinct from invalid request handling
- Unsupported or incomplete creation requests are rejected or clearly flagged before execution
- Higher-layer review surfaces preserve quota, auth, upload, and caveat guidance
- No public MCP tool or hosted behavior changes are introduced in this slice
- Existing Layer 1 execution behavior remains intact outside the endpoint-specific additions
- All new or changed Python functions include reStructuredText docstrings
