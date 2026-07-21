# Quickstart: Layer 2 Tool `videos_list`

## Goal

Verify that YT-247 exposes the low-level `videos_list` tool as an active, endpoint-backed Layer 2 lookup for YouTube video resources.

## Prerequisites

- Work on branch `247-videos-list`.
- Keep the YT-247 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for the contract, validation, result, error, export, and registration behavior.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `videos_list`
   - upstream identity `videos.list`
   - quota cost `1` in metadata, description, usage notes, and examples
   - conditional auth mode
   - API-key-compatible access for `id` and `chart`
   - OAuth-required access for `myRating`
   - active availability state
   - required `part`
   - exactly one selector: `id`, `chart`, or `myRating`
   - pagination allowed only for compatible collection selectors
   - chart-only `regionCode` and `videoCategoryId` refinements
   - empty successful result behavior
   - no video search, upload, update, delete, rating mutation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation
2. Add failing unit tests for:
   - missing `part`
   - empty or non-string `part`
   - missing selector
   - conflicting selectors
   - invalid `id`
   - invalid `chart`
   - invalid `myRating`
   - missing OAuth for `myRating`
   - invalid `pageToken`
   - invalid or out-of-range `maxResults`
   - pagination with direct ID lookup
   - `regionCode` or `videoCategoryId` without chart lookup
   - unsupported search, upload, update, delete, rating mutation, transcript, analytics, recommendation, ranking, summarization, or enrichment fields
   - empty successful results
   - quota, unavailable endpoint, deprecated endpoint, upstream invalid request, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of a valid direct ID lookup
   - dispatcher invocation of a valid chart lookup
   - dispatcher invocation of a valid rating lookup with eligible OAuth context
   - dispatcher rejection or safe categorization of restricted access failure
   - safe error detail sanitization

## Green Phase

1. Add `src/mcp_server/tools/youtube_common/videos.py`.
2. Define the smallest `videos_list` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, auth-context selector, pagination helper, and error mapper needed to pass the focused tests.
3. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Register the descriptor in the default tool catalog.
5. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
6. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, conditional access, selector, pagination, chart refinement, and empty-result guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, signed URLs, or secret-bearing fields.
4. Keep search, captions, video categories, thumbnails, video mutation, rating mutation, analytics, recommendation, and higher-level video workflow behavior out of the videos module.

## Focused Verification

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `videos_list` remains an active, read-only video-resource lookup and does not provide video search, upload, update, delete, rating mutation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or classification behavior.
- Local dispatcher validation may reject requests that miss selectors before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- `id` and `chart` use API-key-compatible access; `myRating` requires OAuth-backed access.
- `pageToken` and `maxResults` apply only to compatible collection selectors.
- `regionCode` and `videoCategoryId` apply only to chart lookup.
- Safe error detail sanitization strips API keys, OAuth tokens, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-247`
- focused test output for `videos_list`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, conditional access, selector behavior, pagination behavior, chart-refinement behavior, and empty-result behavior are visible in metadata, caveats, examples, and safe errors

## Implementation Evidence

- Red check observed before implementation: focused YT-247 tests failed on missing `mcp_server.tools.youtube_common.videos`.
- Focused verification after implementation: `python3 -m pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` reported 317 passed.
- Lint verification after implementation: `python3 -m ruff check .` reported all checks passed.
- Full-suite verification after implementation: `python3 -m pytest` reported 3588 passed.
- Docstring sweep confirmed every new or changed Python function in the YT-247 module and new videos tests has a docstring.
