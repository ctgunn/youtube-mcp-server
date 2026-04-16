# Quickstart: YT-119 Layer 1 Endpoint `comments.setModerationStatus`

## Goal

Add a reviewable internal `comments.setModerationStatus` wrapper on top of the existing Layer 1 foundation with explicit target-comment rules, moderation-state validation, OAuth-required visibility, deterministic optional moderation-flag boundaries, quota visibility, optional delegated-owner guidance if supported, and normalized moderation-acknowledgment outcomes suitable for downstream reuse.

## 1. Review the feature artifacts

- Read the specification: [/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md)
- Read the implementation plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/plan.md)
- Read the research decisions: [/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/research.md)
- Read the wrapper contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-wrapper-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-wrapper-contract.md)
- Read the auth-write contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-auth-write-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-auth-write-contract.md)

## 2. Implement in Red-Green-Refactor order

1. Add failing unit tests for `comments.setModerationStatus` metadata completeness, quota visibility, OAuth enforcement, supported moderation-status validation, optional moderation-flag compatibility, and duplicate-target validation.
2. Add failing transport tests for request construction and normalized result handling for valid, invalid, unsupported-transition, and upstream-rejected moderation profiles.
3. Add failing integration and contract tests showing current wrapper surfaces do not yet make moderation-state behavior, authorization expectations, and normalized upstream failures reviewable enough for downstream feature planning.
4. Implement the smallest updates to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` needed to satisfy those failures.
5. Ensure review surfaces keep operation identity, quota cost, moderation-state rules, authorization expectations, optional moderation-flag boundaries, and upstream-boundary guidance visible without exposing credentials.
6. Refactor for naming clarity and duplication reduction while preserving deterministic moderation validation and normalized outcome boundaries.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

Representative test modules:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`

## 3. Keep scope constrained

- Keep YT-119 internal-only.
- Do not add a public `comments_setModerationStatus` MCP tool in this slice.
- Reuse existing Layer 1 executor and metadata abstractions.
- Focus on moderation-state rules, quota visibility, OAuth-required behavior, optional moderation-flag boundaries, optional delegated-owner guidance if supported, and normalized moderation outcomes.

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

- `comments.setModerationStatus` wrapper metadata shows endpoint identity and quota cost `50`
- Supported moderation states are clear
- OAuth-required behavior is explicit and public-only moderation access is not implied
- Optional moderation-flag boundaries are documented clearly
- Optional delegated-owner inputs are documented if supported for this slice
- Missing authorization and malformed moderation requests fail clearly
- Unsupported moderation-state or flag combinations are rejected clearly
- Normalized upstream moderation failures remain distinguishable from local validation failures
- No public MCP or hosted behavior changes are introduced
- All new or changed Python functions include reStructuredText docstrings
