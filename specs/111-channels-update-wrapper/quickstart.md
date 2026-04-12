# Quickstart: YT-111 Layer 1 Endpoint `channels.update`

## Goal

Add a reviewable internal `channels.update` wrapper on top of the existing Layer 1 foundation with explicit writable-part rules for `brandingSettings` and `localizations`, OAuth-required visibility, deterministic update validation, quota visibility, and normalized update outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/contracts/layer1-channels-update-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/contracts/layer1-channels-update-wrapper-contract.md)
- Read the auth-write contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/contracts/layer1-channels-update-auth-write-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/contracts/layer1-channels-update-auth-write-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `channels.update` metadata completeness, quota visibility, writable-part validation, and OAuth-required enforcement.
2. Add failing transport tests for `PUT` request construction and normalized result handling for valid and invalid channel-update profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make write boundaries reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, writable-part rules, OAuth-required behavior, and invalid-write guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic write validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative implementation modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`

## 3. Keep scope constrained

- Keep YT-111 internal-only.
- Do not add a public `channels_update` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on writable-part rules, OAuth-required behavior, quota visibility, and normalized update outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest tests/contract/test_layer1_channels_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `channels.update` wrapper metadata shows endpoint identity and quota cost `50`
- Supported writable parts (`brandingSettings` and `localizations`) and part-to-body alignment rules are clear
- OAuth-required behavior is documented explicitly
- Unsupported or read-only update fields fail clearly
- Auth failures are distinct from invalid write-shape failures
- Updated-resource success remains distinct from normalized failure outcomes
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
