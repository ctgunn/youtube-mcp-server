# Quickstart: YT-121 Layer 1 Endpoint `commentThreads.list`

## Goal

Add a reviewable internal `commentThreads.list` wrapper on top of the existing Layer 1 foundation with explicit selector rules, public-access visibility for the seed-supported paths, deterministic selector validation, quota visibility, and normalized retrieval outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md)
- Read the lookup-auth contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-lookup-auth-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-lookup-auth-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `commentThreads.list` metadata completeness, quota visibility, selector exclusivity, and selector handling across `videoId`, `allThreadsRelatedToChannelId`, and `id`.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, and empty-result selector profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make selector behavior, access expectations, and no-match handling reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, selector rules, access expectations, and empty-result guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic selector validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comment_threads_contract.py`

## 3. Keep scope constrained

- Keep YT-121 internal-only.
- Do not add a public `commentThreads_list` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on selector rules, quota visibility, access expectations for the seed-supported paths, and normalized retrieval outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_comment_threads_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `commentThreads.list` wrapper metadata shows endpoint identity and quota cost `1`
- Supported selectors and selector exclusivity rules are clear
- Video-based, channel-related, and ID-based retrieval are documented as separate supported paths
- Missing-selector and conflicting-selector requests fail clearly
- Access mismatch failures are distinct from validation failures
- Empty result sets for valid requests remain success outcomes
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
