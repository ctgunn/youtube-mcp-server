# Quickstart: YT-113 Layer 1 Endpoint `channelSections.insert`

## Goal

Add a reviewable internal `channelSections.insert` wrapper on top of the existing Layer 1 foundation with explicit section-type rules, OAuth-required visibility, deterministic create validation, quota visibility, optional delegation guidance, and normalized create outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-wrapper-contract.md)
- Read the auth-write contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `channelSections.insert` metadata completeness, quota visibility, OAuth enforcement, and section-type validation across playlist-backed and channel-backed create requests.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, duplicated, and authorization-mismatched create profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make section-type, title, and delegation behavior reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, and any narrowly required companion modules needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, section-type rules, title rules, OAuth behavior, and delegation guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic create validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`

## 3. Keep scope constrained

- Keep YT-113 internal-only.
- Do not add a public `channelSections_insert` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on create-body rules, OAuth-required behavior, quota visibility, section-type guidance, optional delegation inputs, and normalized create outcomes.

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

- `channelSections.insert` wrapper metadata shows endpoint identity and quota cost `50`
- Supported section-type and content-alignment rules are clear
- OAuth-required behavior is explicit and public-only create access is not implied
- Title requirements and optional delegation inputs are documented
- Missing authorization and malformed create requests fail clearly
- Duplicated or unsupported playlists and channels are rejected clearly
- Normalized upstream create failures remain distinguishable from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
