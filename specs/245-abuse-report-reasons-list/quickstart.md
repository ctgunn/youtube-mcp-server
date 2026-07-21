# Quickstart: Layer 2 Tool `videoAbuseReportReasons_list`

## Goal

Validate that `videoAbuseReportReasons_list` is planned, implemented, documented, and verified as a low-level Layer 2 MCP tool for `videoAbuseReportReasons.list`.

## Prerequisites

- Branch: `245-abuse-report-reasons-list`
- Feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/plan.md`
- Layer 1 dependency: `build_video_abuse_report_reasons_list_wrapper()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_abuse_report_reasons.py`
- Shared Layer 2 dependencies: YT-201 and YT-202 contracts

## Implementation Scope

Add `videoAbuseReportReasons_list` to a concrete Layer 2 video-abuse-report-reasons family:

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
```

Expected test locations:

```text
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_video_abuse_report_reasons_registration.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
```

## Red Phase

Create failing tests before implementation:

```bash
pytest tests/contract/test_youtube_video_abuse_report_reasons_contract.py tests/unit/test_youtube_video_abuse_report_reasons.py tests/integration/test_youtube_video_abuse_report_reasons_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

The failing tests should prove `videoAbuseReportReasons_list` is missing or incomplete until it provides:

- Public tool name `videoAbuseReportReasons_list`
- Upstream identity `videoAbuseReportReasons.list`
- Quota cost `1` in metadata, description, usage notes, examples, and result context
- API-key access disclosure and safe access failure handling
- Input schema requiring `part` and `hl`
- Validation for missing, empty, malformed, unsupported, and extra fields
- Localization context preservation for `hl`
- Successful populated and empty reason-list results
- Safe quota, access, availability, deprecation, and upstream failure categories
- Default registry discovery and dispatcher execution
- reStructuredText docstrings for every new or changed Python function

## Green Phase

Implement the smallest endpoint-backed tool that passes the focused tests:

- Add video-abuse-report-reasons list constants, schema, description, usage notes, caveats, examples, contract builder, descriptor builder, validator, handler, result mapper, and upstream-error mapper.
- Use the existing Layer 1 `build_video_abuse_report_reasons_list_wrapper()`.
- Require API-key access context before execution.
- Map success to a reason-list result with safe requested parts, localization, quota, endpoint, access, and item context.
- Preserve empty item collections as successful lookups.
- Export video-abuse-report-reasons symbols and register the tool with the default catalog.

## Refactor Phase

After focused tests pass:

- Remove duplication with existing read/list and localization helpers where it improves clarity without broad refactoring.
- Preserve all new and changed reStructuredText docstrings.
- Confirm errors sanitize credentials, authorization headers, raw upstream diagnostics, stack traces, and unsafe request context.
- Confirm the tool remains narrow and does not add abuse report submission, report status lookup, moderation action, policy adjudication, video lookup, ranking, summarization, enrichment, analytics, bulk processing, or cross-endpoint behavior.

## Verification Commands

Focused verification:

```bash
pytest tests/contract/test_youtube_video_abuse_report_reasons_contract.py tests/unit/test_youtube_video_abuse_report_reasons.py tests/integration/test_youtube_video_abuse_report_reasons_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
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

- Discovery metadata identifies `videoAbuseReportReasons_list`, `videoAbuseReportReasons.list`, quota `1`, API-key access, required `part`, required `hl`, localization behavior, empty-result behavior, and active availability.
- Examples cover localized reason lookup, populated success, empty success, missing `part`, missing `hl`, invalid `part`, invalid `hl`, missing access, quota or upstream failure, and out-of-scope report-submission request rejection.
- Result shape acknowledges reason-catalog lookup without fabricating labels, descriptions, policy interpretations, moderation outcomes, report status, rankings, summaries, or enrichment.
- Failure details never expose credentials, authorization headers, stack traces, raw upstream payloads, or unsafe request context.
- Pull request evidence includes focused test output, full `pytest` output, `ruff check .` output, and docstring review notes.

## Implementation Evidence

- Focused verification completed with `python3 -m pytest tests/contract/test_youtube_video_abuse_report_reasons_contract.py tests/unit/test_youtube_video_abuse_report_reasons.py tests/integration/test_youtube_video_abuse_report_reasons_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`: 282 passed.
- Quality check completed with `python3 -m ruff check .`: all checks passed.
- Full repository verification completed with `python3 -m pytest`: 3437 passed.
- Docstring audit confirmed all functions and classes in `src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py` and `tests/unit/test_youtube_video_abuse_report_reasons.py` have docstrings.
