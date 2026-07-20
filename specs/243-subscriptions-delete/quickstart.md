# Quickstart: Layer 2 Subscriptions Delete Tool

## Goal

Validate that `subscriptions_delete` is planned, implemented, documented, and verified as a low-level Layer 2 MCP tool for `subscriptions.delete`.

## Prerequisites

- Branch: `243-subscriptions-delete`
- Feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/plan.md`
- Layer 1 dependency: `build_subscriptions_delete_wrapper()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py`
- Shared Layer 2 dependencies: YT-201 and YT-202 contracts

## Implementation Scope

Add `subscriptions_delete` to the existing Layer 2 subscriptions family:

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
```

Expected test locations:

```text
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
```

## Red Phase

Create failing tests before implementation:

```bash
pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

The failing tests should prove `subscriptions_delete` is missing or incomplete until it provides:

- Public tool name `subscriptions_delete`
- Upstream identity `subscriptions.delete`
- Quota cost `50` in metadata, description, usage notes, examples, and result context
- OAuth-required access disclosure and enforcement
- Input schema requiring only `id`
- Validation for missing, empty, malformed, unsupported, and extra fields
- Safe deletion acknowledgment result
- Safe target-state and upstream failure categories
- Default registry discovery and dispatcher execution
- reStructuredText docstrings for every new or changed Python function

## Green Phase

Implement the smallest endpoint-backed tool that passes the focused tests:

- Add delete constants, schema, description, usage notes, caveats, examples, contract builder, descriptor builder, validator, handler, result mapper, and upstream-error mapper.
- Use the existing Layer 1 `build_subscriptions_delete_wrapper()`.
- Require OAuth before execution.
- Map success to a deletion acknowledgment with safe `id`, quota, endpoint, and auth context.
- Export delete symbols and register the tool with the default catalog.

## Refactor Phase

After focused tests pass:

- Remove duplication with existing list/insert helpers where it improves clarity without broad refactoring.
- Preserve all new and changed reStructuredText docstrings.
- Confirm errors sanitize credentials and raw upstream diagnostics.
- Confirm the tool remains narrow and does not add listing, creation, lookup, enrichment, analytics, recommendation, notification, or bulk behavior.

## Verification Commands

Focused verification:

```bash
pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Full repository behavior check:

```bash
pytest
```

Repository quality check:

```bash
ruff check .
```

## Manual Review Checklist

- Discovery metadata identifies `subscriptions_delete`, `subscriptions.delete`, quota `50`, OAuth-required access, and active availability.
- Examples cover successful deletion, missing id, empty id, missing OAuth, already-removed or missing target, non-removable target, quota/upstream failure, and out-of-scope workflow rejection.
- Result shape acknowledges deletion without fabricating subscription or channel details.
- Failure details never expose credentials, authorization headers, stack traces, raw upstream payloads, or unsafe request context.
- Pull request evidence includes focused test output, full `pytest` output, `ruff check .` output, and docstring review notes.

## Implementation Evidence

- Focused verification completed with `python3 -m pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`: 302 passed.
- Repository quality check completed with `python3 -m ruff check .`: all checks passed.
- Full repository behavior check completed with `python3 -m pytest`: 3315 passed.
- Docstring review completed for new and modified Python functions in `src/mcp_server/tools/youtube_common/subscriptions.py` and test helper methods in `tests/unit/test_youtube_subscriptions.py`.
