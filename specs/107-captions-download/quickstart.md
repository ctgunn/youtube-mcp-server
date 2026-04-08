# Quickstart: YT-107 Layer 1 Endpoint `captions.download`

## Goal

Use this feature to add a reviewable internal `captions.download` wrapper on top of the existing Layer 1 foundation, with clear quota visibility, explicit permission guidance, visible OAuth and delegation notes, deterministic download-option validation, and a stable distinction between inaccessible and nonexistent caption tracks.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/plan.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts/layer1-captions-download-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts/layer1-captions-download-wrapper-contract.md)
- Read the access and format contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts/layer1-captions-download-access-format-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts/layer1-captions-download-access-format-contract.md)

## 2. Implement the feature in Red-Green-Refactor order

1. Add failing unit tests for `captions.download` metadata completeness, quota visibility, required caption-track identification, optional `tfmt` and `tlang` handling, and OAuth-only enforcement.
2. Add failing contract tests for maintainer-facing artifacts that must explain permission sensitivity, optional delegation guidance, and the supported boundary for download format and translation options.
3. Add failing integration and transport tests showing the representative wrapper path does not yet make `captions.download` reusable for transcript-oriented planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and any narrowly necessary supporting integration modules needed to satisfy those failures.
5. Ensure the wrapper review surface exposes endpoint identity, `quotaCost`, OAuth-required guidance, permission-sensitive notes, the supported `tfmt` and `tlang` boundary, and `onBehalfOfContentOwner` guidance clearly enough for later transcript and caption-delivery work.
6. Update higher-layer review flows so consumer-facing summaries can expose `captions.download` source operation, quota, auth mode, permission notes, supported output options, and the stable `access-denied` versus `not-found` failure boundary without leaking raw upstream details or downloaded caption payloads.
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

- Keep YT-107 internal-only.
- Do not add a public `captions_download` MCP tool here; that belongs to later Layer 2 work.
- Reuse the YT-101 executor and YT-102 metadata standards instead of inventing a second endpoint-wrapper abstraction.
- Focus on identifier validation, permission visibility, format and translation option clarity, auth visibility, delegation visibility, quota visibility, and download-result handling rather than broader transcript feature expansion.

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

- `captions.download` wrapper metadata shows endpoint identity and the quota cost of `200`
- Maintainer-facing artifacts state that authorized access is required
- Supported request inputs identify the caption track and the documented optional `tfmt` and `tlang` modifiers
- Permission-sensitive behavior is visible before reuse
- Optional `onBehalfOfContentOwner` guidance is visible before reuse
- Unsupported or incomplete download requests are rejected or clearly flagged before execution
- `access-denied` and `not-found` failure outcomes remain distinguishable for higher-layer reuse
- Higher-layer review surfaces preserve quota, auth, and download-option guidance
- No public MCP tool or hosted behavior changes are introduced in this slice
- Existing Layer 1 execution behavior remains intact outside the endpoint-specific additions
- All new or changed Python functions include reStructuredText docstrings
