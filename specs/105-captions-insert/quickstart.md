# Quickstart: YT-105 Layer 1 Endpoint `captions.insert`

## Goal

Use this feature to add a reviewable internal `captions.insert` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit `body` plus `media` guidance, visible OAuth and delegation notes, and deterministic rejection of unsupported request combinations.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/plan.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts/layer1-captions-insert-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts/layer1-captions-insert-wrapper-contract.md)
- Read the auth and upload contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts/layer1-captions-insert-auth-upload-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts/layer1-captions-insert-auth-upload-contract.md)

## 2. Implement the feature in Red-Green-Refactor order

1. Add failing unit tests for `captions.insert` metadata completeness, quota visibility, metadata-plus-upload validation, and OAuth-only enforcement.
2. Add failing contract tests for maintainer-facing artifacts that must explain upload sensitivity, optional delegation guidance, and the boundary between valid create requests and invalid incomplete requests.
3. Add failing integration and transport tests showing the representative wrapper path does not yet make `captions.insert` reusable for higher-layer planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and any narrowly necessary supporting integration modules needed to satisfy those failures.
5. Ensure the wrapper review surface exposes endpoint identity, `quotaCost`, OAuth-required guidance, the supported `body` plus `media` boundary, and `onBehalfOfContentOwner` notes clearly enough for later caption-management work.
6. Update higher-layer review flows so consumer-facing summaries can expose `captions.insert` source operation, quota, auth mode, and upload guidance without leaking raw upstream details or media content.
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
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`

## 3. Keep the change scoped

- Keep YT-105 internal-only.
- Do not add a public `captions_insert` MCP tool here; that belongs to later Layer 2 work.
- Reuse the YT-101 executor and YT-102 metadata standards instead of inventing a second endpoint-wrapper abstraction.
- Focus on metadata-plus-upload validation, auth visibility, delegation visibility, quota visibility, and created-resource handling rather than broad caption-management expansion.

## 4. Verify before review

Run the targeted and full validation steps expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_captions_contract.py
python3 -m pytest tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `captions.insert` wrapper metadata shows endpoint identity and the quota cost of `400`
- Maintainer-facing artifacts state that authorized access is required
- Supported request inputs distinguish the required `body` metadata payload from the required `media` upload payload
- Optional `onBehalfOfContentOwner` guidance is visible before reuse
- Unsupported or incomplete creation requests are rejected or clearly flagged before execution
- Higher-layer review surfaces preserve quota, auth, and upload guidance
- No public MCP tool or hosted behavior changes are introduced in this slice
- Existing Layer 1 execution behavior remains intact outside the endpoint-specific additions
- All new or changed Python functions include reStructuredText docstrings
