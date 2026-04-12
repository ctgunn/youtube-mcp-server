# Quickstart: YT-112 Layer 1 Endpoint `channelSections.list`

## Goal

Add a reviewable internal `channelSections.list` wrapper on top of the existing Layer 1 foundation with explicit selector rules, mixed-auth visibility, deterministic selector validation, quota visibility, and normalized retrieval outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-wrapper-contract.md)
- Read the auth-filter contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-auth-filter-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-auth-filter-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `channelSections.list` metadata completeness, quota visibility, selector exclusivity, and selector-auth compatibility across `channelId`, `id`, and `mine`.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, and empty-result selector profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make selector/auth behavior and lifecycle-note handling reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, selector rules, mixed-auth behavior, and lifecycle-note guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic selector validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`

## 3. Keep scope constrained

- Keep YT-112 internal-only.
- Do not add a public `channelSections_list` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on selector rules, mixed-auth behavior, quota visibility, lifecycle-note readiness, and normalized retrieval outcomes.

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

- `channelSections.list` wrapper metadata shows endpoint identity and quota cost `1`
- Supported selectors and selector exclusivity rules are clear
- Selector-auth behavior is documented as mixed or conditional with explicit `mine` owner-scoped expectations
- Missing-selector and conflicting-selector requests fail clearly
- Auth mismatch failures are distinct from validation failures
- Empty result sets for valid requests remain success outcomes
- Lifecycle-note guidance is visible when availability or deprecation caveats matter
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
