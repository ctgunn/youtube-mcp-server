# Quickstart: YT-108 Layer 1 Endpoint `captions.delete`

## Goal

Use this feature to add a reviewable internal `captions.delete` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit ownership guidance, visible OAuth and delegation notes, deterministic delete-input validation, and a stable distinction between inaccessible and nonexistent caption tracks.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/plan.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-wrapper-contract.md)
- Read the authorization contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-auth-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-auth-contract.md)

## 2. Implement the feature in Red-Green-Refactor order

1. Add failing unit tests for `captions.delete` metadata completeness, quota visibility, required caption-track identification, optional delegation handling, and OAuth-only enforcement.
2. Add failing contract tests for maintainer-facing artifacts that must explain ownership sensitivity, optional delegation guidance, and the supported boundary for caption deletion.
3. Add failing integration and transport tests showing the representative wrapper path does not yet make `captions.delete` reusable for caption-management planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and any narrowly necessary supporting integration modules needed to satisfy those failures.
5. Ensure the wrapper review surface exposes endpoint identity, `quotaCost`, OAuth-required guidance, ownership-sensitive notes, and `onBehalfOfContentOwner` guidance clearly enough for later caption-management work.
6. Update higher-layer review flows so consumer-facing summaries can expose `captions.delete` source operation, quota, auth mode, ownership notes, a normalized delete outcome, and the stable `access-denied` versus `not-found` failure boundary without leaking raw upstream details or secrets.
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

- Keep YT-108 internal-only.
- Do not add a public `captions_delete` MCP tool here; that belongs to later Layer 2 work.
- Reuse the YT-101 executor and YT-102 metadata standards instead of inventing a second endpoint-wrapper abstraction.
- Focus on identifier validation, ownership visibility, auth visibility, delegation visibility, quota visibility, and delete-result handling rather than broader caption-management feature expansion.

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

- `captions.delete` wrapper metadata shows endpoint identity and the quota cost of `50`
- Maintainer-facing artifacts state that authorized access is required
- Supported request inputs identify one caption track and the documented optional `onBehalfOfContentOwner` delegation input
- Ownership-sensitive behavior is visible before reuse
- Successful deletion remains reviewable through a normalized result even when the upstream body is empty
- Unsupported or incomplete delete requests are rejected or clearly flagged before execution
- `access-denied` and `not-found` failure outcomes remain distinguishable for higher-layer reuse
- Higher-layer review surfaces preserve quota, auth, and ownership guidance
- No public MCP tool or hosted behavior changes are introduced in this slice
- Existing Layer 1 execution behavior remains intact outside the endpoint-specific additions
- All new or changed Python functions include reStructuredText docstrings
