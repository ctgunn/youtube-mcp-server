# Quickstart: YT-115 Layer 1 Endpoint `channelSections.delete`

## Goal

Add a reviewable internal `channelSections.delete` wrapper on top of the existing Layer 1 foundation with explicit delete-target rules, OAuth-required visibility, optional delegation guidance, higher-layer delete summaries, quota visibility, and normalized delete outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-wrapper-contract.md)
- Read the auth-delete contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-auth-delete-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-auth-delete-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `channelSections.delete` metadata completeness, quota visibility, required delete-target identity, optional delegation handling, and OAuth enforcement.
2. Add failing transport tests for `DELETE` request construction and normalized result handling for valid, delegated, unauthorized, and unavailable-target delete profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make delete-target boundaries, OAuth behavior, target-state guidance, and higher-layer delete summaries reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, and any narrowly required companion modules needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, delete-target rules, OAuth behavior, optional delegation guidance, and target-state failure interpretation visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic delete validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

## 3. Keep scope constrained

- Keep YT-115 internal-only.
- Do not add a public `channelSections_delete` MCP tool in this slice.
- Reuse existing Layer 1 executor, metadata, transport, and higher-layer summary abstractions.
- Focus on delete-target identity, OAuth-required behavior, optional delegation inputs, higher-layer delete summaries, and normalized delete outcomes.

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

- `channelSections.delete` wrapper metadata shows endpoint identity and quota cost `50`
- Supported delete boundary is clear and scoped to one target section
- OAuth-required behavior is explicit and public delete access is not implied
- Optional delegation inputs are documented
- Missing authorization and malformed delete requests fail clearly
- Unavailable or already-removed targets are distinguishable from local validation failures
- Higher-layer delete summaries remain reviewable and source-operation aware
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
