# Quickstart: YT-220 Layer 2 Tool `comments_delete`

## Goal

Implement the public Layer 2 `comments_delete` MCP tool so callers can delete one existing YouTube comment through the endpoint-backed `comments.delete` operation with visible quota, OAuth, target-comment, destructive-deletion, request validation, acknowledgment, and error behavior.

## Read First

- Spec: [/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/spec.md)
- Plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/plan.md)
- Research: [/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/research.md)
- Data model: [/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/data-model.md)
- Contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/contracts/comments-delete-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/contracts/comments-delete-tool-contract.md)

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

Expected initial failures should prove `comments_delete` is not yet exported, registered, discoverable, described, executable, validated, or safely mapped as a public Layer 2 tool.

## Green Phase

Implement the minimum endpoint-backed public tool behavior:

- Constants for tool name, quota cost, schema, description, usage notes, caveats, and examples.
- Contract builder exposing `comments.delete`, quota cost 50, OAuth-required auth, active availability, near-raw response boundary, and destructive mutation acknowledgment response convention.
- Tool descriptor and handler that require OAuth, call the Layer 1 wrapper, and map 204/no-content success to a safe deletion acknowledgment.
- Validation for required `id`, empty or malformed `id`, duplicate or conflicting target shapes, unsupported request body, unsupported optional parameters, and unsafe workflow fields.
- Error mapping for invalid request, missing OAuth, insufficient authorization, quota exhaustion, missing or already deleted target comments, endpoint unavailable, deprecation, and unexpected upstream failure.
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

- Matched seed slice: `YT-220`.
- Dependency assumptions: YT-120, YT-201, and YT-202.
- Focused failing tests from Red phase.
- Focused passing tests from Green and Refactor phases.
- Full `pytest` result after final code changes.
- `ruff check .` result after final code changes.
- Any official documentation caveats found while implementing `comments_delete`.

## Implementation Evidence

Recorded on 2026-06-19:

- Red scaffold check: bare `pytest` was not available on PATH; reran with `python3 -m pytest` and observed the expected missing `build_comments_delete_tool_descriptor` import failure before Green implementation.
- Green/refactor comments check: `python3 -m pytest tests/unit/test_youtube_comments.py tests/contract/test_youtube_comments_contract.py` passed with 173 tests.
- Focused feature suite: `python3 -m pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` passed with 300 tests.
- Full repository suite: `python3 -m pytest` passed with 2234 tests.
- Lint: `python3 -m ruff check .` passed.
