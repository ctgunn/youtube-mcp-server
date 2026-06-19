# Quickstart: YT-218 Layer 2 Tool `comments_update`

## Goal

Implement the public Layer 2 `comments_update` MCP tool so callers can edit an existing YouTube comment through the endpoint-backed `comments.update` operation with visible quota, OAuth, writable-field, request validation, result, and error behavior.

## Read First

- Spec: [/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/spec.md)
- Plan: [/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/plan.md)
- Research: [/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/research.md)
- Data model: [/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/data-model.md)
- Contract: [/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/contracts/comments-update-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/contracts/comments-update-tool-contract.md)

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

Expected initial failures should prove `comments_update` is not yet exported, registered, discoverable, described, executable, validated, or safely mapped.

## Green Phase

Implement the minimum endpoint-backed public tool behavior:

- Constants for tool name, quota cost, supported parts, schema, description, usage notes, caveats, and examples.
- Contract builder exposing `comments.update`, quota cost 50, OAuth-required auth, active availability, near-raw response boundary, and updated-resource response convention.
- Tool descriptor and handler that require OAuth, call the Layer 1 wrapper, and map success to a safe near-raw updated comment result.
- Validation for required `part`, required `body.id`, required `body.snippet.textOriginal`, unsupported parts, read-only body fields, unsupported optional parameters, and unsafe workflow fields.
- Error mapping for invalid request, missing OAuth, insufficient authorization, quota exhaustion, missing target comment, endpoint unavailable, deprecation, and unexpected upstream failure.
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

- Matched seed slice: `YT-218`.
- Dependency assumptions: YT-118, YT-201, and YT-202.
- Focused failing tests from Red phase.
- Focused passing tests from Green and Refactor phases.
- Full `pytest` result after final code changes.
- `ruff check .` result after final code changes.
- Any official documentation caveats found while implementing `comments_update`.

## Implementation Evidence

Recorded 2026-06-18:

- Matched seed slice: `YT-218`.
- Focused Red evidence: `comments_update` foundational checks failed for missing exports, representative catalog entry, and default registry discovery before implementation.
- Focused Green/Refactor evidence: `PYTHONPATH=/Users/ctgunn/Projects/youtube-mcp-server/src python3 -m pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` passed with 209 tests.
- Lint evidence: `PYTHONPATH=/Users/ctgunn/Projects/youtube-mcp-server/src python3 -m ruff check .` passed.
- Full-suite evidence: `PYTHONPATH=/Users/ctgunn/Projects/youtube-mcp-server/src python3 -m pytest` passed with 2143 tests.
