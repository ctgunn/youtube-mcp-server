# Quickstart: YT-219 Layer 2 Tool `comments_setModerationStatus`

## Goal

Implement the public Layer 2 `comments_setModerationStatus` MCP tool so callers can set moderation status for one or more existing YouTube comments through the endpoint-backed `comments.setModerationStatus` operation with visible quota, OAuth, moderation-state, optional-flag, request validation, acknowledgment, and error behavior.

## Read First

- Spec: [/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/spec.md)
- Plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/plan.md)
- Research: [/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/research.md)
- Data model: [/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/data-model.md)
- Contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/contracts/comments-set-moderation-status-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/contracts/comments-set-moderation-status-tool-contract.md)

## Implementation Entry Points

- Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`.
- Export public symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
- Register the descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` if default registry integration is not already centralized through the comments family.
- Reuse Layer 1 endpoint behavior from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`.

## Red Phase

Add failing tests before implementation:

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected initial failures should prove `comments_setModerationStatus` is not yet exported, registered, discoverable, described, executable, validated, or safely mapped as a public Layer 2 tool.

## Green Phase

Implement the minimum endpoint-backed public tool behavior:

- Constants for tool name, quota cost, supported moderation statuses, schema, description, usage notes, caveats, and examples.
- Contract builder exposing `comments.setModerationStatus`, quota cost 50, OAuth-required auth, active availability, near-raw response boundary, and mutation-acknowledgment response convention.
- Tool descriptor and handler that require OAuth, call the Layer 1 wrapper, and map 204/no-content success to a safe moderation acknowledgment.
- Validation for required `id`, duplicate IDs, required `moderationStatus`, supported statuses, boolean `banAuthor`, `banAuthor` only with `rejected`, unsupported request body, unsupported optional parameters, and unsafe workflow fields.
- Error mapping for invalid request, missing OAuth, insufficient authorization, quota exhaustion, missing target comments, limited moderation functionality, endpoint unavailable, deprecation, and unexpected upstream failure.
- Public exports and default registry integration.

Every new or changed Python function must include a reStructuredText docstring documenting purpose, inputs, outputs, relevant raised errors, quota/auth behavior, and side effects where applicable.

## Refactor Phase

After focused tests pass:

- Remove duplicated wording or helper code that belongs in shared YT-201/YT-202 conventions.
- Keep `comments.py` cohesive and avoid unrelated changes to other resource families.
- Preserve safe error and metadata surfaces without leaking API keys, OAuth tokens, stack traces, raw request bodies, or unsafe upstream diagnostics.
- Run the focused suite, full suite, and lint.

## Verification

Focused verification:

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Full repository verification:

```bash
pytest
ruff check .
```

## Review Evidence

Pull request notes should include:

- Matched seed slice: `YT-219`.
- Dependency assumptions: YT-119, YT-201, and YT-202.
- Focused failing tests from Red phase.
- Focused passing tests from Green and Refactor phases.
- Full `pytest` result after final code changes.
- `ruff check .` result after final code changes.
- Any official documentation caveats found while implementing `comments_setModerationStatus`.

## Implementation Evidence

Recorded on `2026-06-18 21:21:08 CDT`.

- Matched seed slice: `YT-219`.
- Dependency assumptions: YT-119, YT-201, and YT-202 remain satisfied by existing Layer 1 comments wrappers and shared Layer 2 contract helpers.
- Red phase: focused scaffold suite failed during collection before implementation because `COMMENTS_SET_MODERATION_STATUS_*`, `build_comments_set_moderation_status_tool_descriptor`, and related public symbols were missing.
- Green and refactor focused suite: `python3 -m pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` passed with `249 passed in 0.80s`.
- Full suite: `python3 -m pytest` passed with `2183 passed in 10.18s`.
- Lint: `python3 -m ruff check .` passed with `All checks passed!`.
- Official documentation caveat reflected in implementation: `comments.setModerationStatus` returns a no-content moderation acknowledgment, so the Layer 2 result exposes safe target/status context without fabricating a comment resource body.
