# Quickstart: Layer 2 Thumbnails Set Tool

## Goal

Validate that `thumbnails_set` is planned, implemented, documented, and verified as a low-level Layer 2 MCP tool for `thumbnails.set`.

## Prerequisites

- Branch: `244-thumbnails-set`
- Feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/plan.md`
- Layer 1 dependency: `build_thumbnails_set_wrapper()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/thumbnails.py`
- Shared Layer 2 dependencies: YT-201 and YT-202 contracts

## Implementation Scope

Add `thumbnails_set` to a concrete Layer 2 thumbnails family:

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
```

Expected test locations:

```text
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_thumbnails_registration.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
```

## Red Phase

Create failing tests before implementation:

```bash
pytest tests/contract/test_youtube_thumbnails_contract.py tests/unit/test_youtube_thumbnails.py tests/integration/test_youtube_thumbnails_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

The failing tests should prove `thumbnails_set` is missing or incomplete until it provides:

- Public tool name `thumbnails_set`
- Upstream identity `thumbnails.set`
- Quota cost `50` in metadata, description, usage notes, examples, and result context
- OAuth-required access disclosure and enforcement
- Input schema requiring `videoId` and `media`
- Validation for missing, empty, malformed, unsupported, and extra fields
- Safe media-upload descriptors that never echo raw upload content
- Safe thumbnail-set result for sparse and populated upstream successes
- Safe target-video, upload, quota, and upstream failure categories
- Default registry discovery and dispatcher execution
- reStructuredText docstrings for every new or changed Python function

## Green Phase

Implement the smallest endpoint-backed tool that passes the focused tests:

- Add thumbnails set constants, schema, description, usage notes, caveats, examples, contract builder, descriptor builder, validator, handler, result mapper, and upstream-error mapper.
- Use the existing Layer 1 `build_thumbnails_set_wrapper()`.
- Require OAuth before execution.
- Map success to a thumbnail-set result with safe `videoId`, upload descriptor, quota, endpoint, and auth context.
- Export thumbnails symbols and register the tool with the default catalog.

## Refactor Phase

After focused tests pass:

- Remove duplication with existing media-upload mutation helpers where it improves clarity without broad refactoring.
- Preserve all new and changed reStructuredText docstrings.
- Confirm errors sanitize credentials, raw upload bytes, and raw upstream diagnostics.
- Confirm the tool remains narrow and does not add thumbnail generation, image editing, video upload, video metadata updates, channel branding, enrichment, analytics, ranking, summarization, preflight lookup, or bulk behavior.

## Verification Commands

Focused verification:

```bash
pytest tests/contract/test_youtube_thumbnails_contract.py tests/unit/test_youtube_thumbnails.py tests/integration/test_youtube_thumbnails_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
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

- Discovery metadata identifies `thumbnails_set`, `thumbnails.set`, quota `50`, OAuth-required access, media-upload requirement, and active availability.
- Examples cover successful thumbnail setting, sparse success handling, missing `videoId`, missing `media`, invalid `videoId`, unsupported upload content, missing OAuth, target-video or quota upstream failure, and out-of-scope workflow rejection.
- Result shape acknowledges thumbnail setting without fabricating thumbnail, video, channel, analytics, or enrichment details.
- Failure details never expose credentials, authorization headers, stack traces, raw upstream payloads, raw upload content, or unsafe request context.
- Pull request evidence includes focused test output, full `pytest` output, `ruff check .` output, and docstring review notes.

## Implementation Evidence

- 2026-07-20: Focused verification passed with `python3 -m pytest tests/contract/test_youtube_thumbnails_contract.py tests/unit/test_youtube_thumbnails.py tests/integration/test_youtube_thumbnails_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` (`283 passed`).
- 2026-07-20: Repository quality passed with `python3 -m ruff check .`.
- 2026-07-20: Full repository behavior passed with `python3 -m pytest` (`3379 passed`).
- 2026-07-20: Python docstring review reported all new and modified helper functions have docstrings.
