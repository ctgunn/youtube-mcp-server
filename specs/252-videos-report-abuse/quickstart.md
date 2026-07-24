# Quickstart: Layer 2 Tool `videos_reportAbuse`

## Goal

Verify that YT-252 exposes the low-level `videos_reportAbuse` tool as an OAuth-required, endpoint-backed Layer 2 mutation tool for submitting an abuse report for one YouTube video.

## Prerequisites

- Work on branch `252-videos-report-abuse`.
- Keep the YT-252 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use fake wrapper payloads, test-safe video identifiers, and test-safe reason IDs; do not use real credentials, private channel data, tokens, authorization headers, raw upstream diagnostics, live YouTube calls, or sensitive report comments in tests or examples.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `videos_reportAbuse`
   - upstream identity `videos.reportAbuse`
   - quota cost `50` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - required `body.videoId`
   - required `body.reasonId`
   - supported optional `body.secondaryReasonId`, `body.comments`, and `body.language`
   - rejected `onBehalfOfContentOwner` in this slice
   - no-content acknowledgment success result
   - no abuse-reason discovery, automated abuse classification, evidence gathering, moderation decision, metadata lookup/update, rating lookup/mutation, deletion, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation
2. Add failing unit tests for:
   - missing `body`
   - non-object `body`
   - missing `body.videoId`
   - empty or non-string `body.videoId`
   - missing `body.reasonId`
   - empty or non-string `body.reasonId`
   - empty or non-string optional body fields
   - unsupported body fields
   - unsupported top-level fields
   - rejected `onBehalfOfContentOwner`
   - missing OAuth
   - safe no-content acknowledgment mapping
   - quota, authorization, forbidden, not-found, unavailable endpoint, deprecated endpoint, upstream refusal, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of valid authorized report submission
   - dispatcher preservation of submitted target and reason context
   - dispatcher rejection of missing body, missing target, missing reason, and unsupported fields
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Extend `src/mcp_server/tools/youtube_common/videos.py`.
2. Define the smallest `videos_reportAbuse` constants, schema, contract builder, descriptor builder, examples, validator, handler, acknowledgment result mapper, OAuth-context selector, default executor, and error mapper needed to pass focused tests.
3. Import and use `build_videos_report_abuse_wrapper()` from the existing Layer 1 videos resource module.
4. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
5. Register the descriptor in the default tool catalog.
6. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, report body, optional body field, no-content acknowledgment, partner-delegation boundary, and unsupported-workflow guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw request context, authorization headers, secret-bearing fields, or sensitive report comments beyond safe caller context.
4. Keep abuse-reason discovery, automated abuse classification, evidence gathering, moderation decisions, metadata lookup/update, rating lookup/mutation, deletion, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, and higher-level video workflow behavior out of the videos report-abuse path.

## Focused Verification

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If implementation touches the Layer 1 videos wrapper, also run:

```bash
pytest tests/contract/test_layer1_videos_contract.py tests/contract/test_layer1_metadata_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `videos_reportAbuse` remains a low-level abuse-report submission tool and does not provide reason discovery, classification, evidence collection, moderation decisions, metadata lookup/update, rating lookup/mutation, deletion, thumbnails, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, or policy enforcement behavior.
- Local dispatcher validation may reject requests that miss required `body` before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Every supported request requires OAuth-backed access.
- The supported request body requires `videoId` and `reasonId`.
- The only supported optional body fields in this slice are `secondaryReasonId`, `comments`, and `language`.
- `onBehalfOfContentOwner` is rejected or left unexposed in this slice because the existing Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Successful report behavior is represented by a structured no-content acknowledgment, not by a refreshed video resource, moderation decision, abuse classification, deletion result, or evidence record.
- Safe result summaries may mention target video identity, submitted reason identifier, optional field presence, quota cost, access mode, and acknowledgment outcome, but must not expose credentials, authorization headers, raw upstream diagnostics, secret-bearing context, or sensitive report text beyond safe caller context.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

- 2026-07-24 Red check:
  `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py`
  failed during collection because `mcp_server.tools.youtube_common.videos` did not yet export `VIDEOS_REPORT_ABUSE_CALLER_EXAMPLES`.
- 2026-07-24 Focused Green check:
  `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py`
  passed with 678 tests.
- 2026-07-24 Focused quickstart verification:
  `pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`
  could not run because `pytest` is not on PATH in this shell. Equivalent module invocation
  `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`
  passed with 678 tests.
- 2026-07-24 Code-quality verification:
  `ruff check .` could not run because `ruff` is not on PATH in this shell. Equivalent module invocation
  `python3 -m ruff check .` passed.
- 2026-07-24 Full repository verification:
  `PYTHONPATH=src python3 -m pytest` passed with 3949 tests.

Pull request notes should include:

- matched seed slice `YT-252`
- focused test output for `videos_reportAbuse`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, OAuth access, body payload boundaries, no-content acknowledgment behavior, rejected partner delegation, safe error categories, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors
