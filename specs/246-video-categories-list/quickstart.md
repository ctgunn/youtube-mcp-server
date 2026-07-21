# Quickstart: Layer 2 Tool `videoCategories_list`

## Goal

Verify that YT-246 exposes the low-level `videoCategories_list` tool as an active, endpoint-backed Layer 2 lookup for YouTube video categories.

## Prerequisites

- Work on branch `246-video-categories-list`.
- Keep the YT-246 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for the contract, validation, result, error, export, and registration behavior.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `videoCategories_list`
   - upstream identity `videoCategories.list`
   - quota cost `1` in metadata, description, usage notes, and examples
   - auth mode `api_key`
   - active availability state
   - required `part`
   - exactly one selector: `regionCode` or `id`
   - optional `hl` display-language behavior
   - empty successful result behavior
   - no video search, category recommendation, analytics, ranking, summarization, enrichment, or automatic classification
2. Add failing unit tests for:
   - missing `part`
   - empty or non-string `part`
   - missing selector
   - conflicting selectors
   - invalid `regionCode`
   - invalid `id`
   - invalid `hl`
   - unsupported paging, ordering, search, video, channel, analytics, classification, recommendation, ranking, summarization, or enrichment fields
   - empty successful results
   - quota, unavailable endpoint, deprecated endpoint, upstream invalid request, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of a valid region lookup
   - dispatcher invocation of a valid ID lookup
   - dispatcher invocation of a localized lookup
   - safe error detail sanitization

## Green Phase

1. Add `src/mcp_server/tools/youtube_common/video_categories.py`.
2. Define the smallest `videoCategories_list` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, and error mapper needed to pass the focused tests.
3. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Register the descriptor in the default tool catalog.
5. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
6. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, API-key access, selector, region, localization, and empty-result guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, signed URLs, or secret-bearing fields.
4. Keep deprecated guide categories, videos, search, analytics, recommendations, and higher-level category workflow behavior out of the video-categories module.

## Focused Verification

```bash
pytest tests/contract/test_youtube_video_categories_contract.py tests/unit/test_youtube_video_categories.py tests/integration/test_youtube_video_categories_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `videoCategories_list` remains an active, read-only video-category lookup and does not provide video search, automatic category selection, category recommendation, analytics, ranking, summarization, enrichment, or classification behavior.
- Local dispatcher validation may reject requests that miss both selectors before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Safe error detail sanitization strips API keys, OAuth tokens, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-246`
- focused test output for `videoCategories_list`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, API-key access, selector behavior, localization behavior, and empty-result behavior are visible in metadata, caveats, examples, and safe errors
