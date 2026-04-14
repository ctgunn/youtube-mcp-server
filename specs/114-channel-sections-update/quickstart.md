# Quickstart: YT-114 Layer 1 Endpoint `channelSections.update`

## Goal

Add a reviewable internal `channelSections.update` wrapper on top of the existing Layer 1 foundation with explicit writable update rules, OAuth-required visibility, deterministic target-section validation, optional delegation guidance, quota visibility, and normalized update outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/contracts/layer1-channel-sections-update-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/contracts/layer1-channel-sections-update-wrapper-contract.md)
- Read the auth-write contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/contracts/layer1-channel-sections-update-auth-write-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/contracts/layer1-channel-sections-update-auth-write-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `channelSections.update` metadata completeness, quota visibility, OAuth enforcement, target-section identity requirements, and section-type-aware update validation.
2. Add failing transport tests for `PUT` request construction and normalized result handling for valid, invalid, duplicated, delegation-aware, and authorization-mismatched update profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make writable update boundaries, title rules, and delegation behavior reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, and any narrowly required companion modules needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, writable field rules, title rules, OAuth behavior, and optional delegation guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic update validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`

## 3. Keep scope constrained

- Keep YT-114 internal-only.
- Do not add a public `channelSections_update` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on update-body identity rules, OAuth-required behavior, writable field guidance, optional delegation inputs, and normalized update outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest tests/contract/test_layer1_channel_sections_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `channelSections.update` wrapper metadata shows endpoint identity and quota cost `50`
- Supported writable update boundaries are clear
- OAuth-required behavior is explicit and public-only update access is not implied
- Title requirements and optional delegation inputs are documented
- Missing authorization and malformed update requests fail clearly
- Duplicated or unsupported playlists and channels are rejected clearly
- Normalized upstream update failures remain distinguishable from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
