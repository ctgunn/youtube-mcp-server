# Quickstart: YT-122 Layer 1 Endpoint `commentThreads.insert`

## Goal

Add a reviewable internal `commentThreads.insert` wrapper on top of the existing Layer 1 foundation with explicit video-targeted top-level-thread-create rules, OAuth-required visibility, deterministic create validation, quota visibility, optional delegation guidance, and normalized create outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-wrapper-contract.md)
- Read the auth-write contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-auth-write-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-auth-write-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `commentThreads.insert` metadata completeness, quota visibility, OAuth enforcement, and top-level-thread body validation for supported create requests.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, target-ineligible, and upstream-rejected top-level thread-create profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make top-level behavior, authorization expectations, and target-eligibility handling reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, `body.snippet.videoId`, `body.snippet.topLevelComment.snippet.textOriginal`, authorization expectations, delegation guidance, and target-eligibility notes visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic create validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comment_threads_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

## 3. Keep scope constrained

- Keep YT-122 internal-only.
- Do not add a public `commentThreads_insert` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on the video-targeted top-level create rules, quota visibility, OAuth-required behavior, optional `onBehalfOfContentOwner` guidance, target-eligibility handling, and normalized create outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_comment_threads_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `commentThreads.insert` wrapper metadata shows endpoint identity and quota cost `50`
- Supported top-level-thread-create rules are clear
- OAuth-required behavior is explicit and public-only create access is not implied
- Optional delegation inputs are documented if supported for this slice
- Missing authorization and malformed create requests fail clearly
- Unsupported reply-style or mixed create shapes are rejected clearly
- Target-eligibility failures remain distinguishable from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
