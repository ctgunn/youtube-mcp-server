# Quickstart: YT-118 Layer 1 Endpoint `comments.update`

## Goal

Add a reviewable internal `comments.update` wrapper on top of the existing Layer 1 foundation with explicit `body.id` and `body.snippet.textOriginal` writable-field rules, OAuth-required visibility, deterministic update validation, quota visibility, optional delegation guidance if supported, and normalized update outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-wrapper-contract.md)
- Read the auth-write contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-auth-write-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-auth-write-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `comments.update` metadata completeness, quota visibility, OAuth enforcement, and writable-field validation for supported comment-edit requests.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, immutable-field, and upstream-rejected comment-update profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make writable-field behavior, authorization expectations, and normalized upstream failures reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, writable-field rules, authorization expectations, and upstream-boundary guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic update validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`

## 3. Keep scope constrained

- Keep YT-118 internal-only.
- Do not add a public `comments_update` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on writable-field rules, quota visibility, OAuth-required behavior, optional delegation guidance if supported, and normalized update outcomes.

## 4. Verify before review

Run targeted and full validation expected by the constitution:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest tests/contract/test_layer1_comments_contract.py
python3 -m pytest
ruff check .
```

## 5. Review readiness checklist

- `comments.update` wrapper metadata shows endpoint identity and quota cost `50`
- Supported writable-field rules are clear
- OAuth-required behavior is explicit and public-only update access is not implied
- Optional delegation inputs are documented if supported for this slice
- Missing authorization and malformed update requests fail clearly
- Unsupported or read-only field edits are rejected clearly
- Normalized upstream update failures remain distinguishable from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
