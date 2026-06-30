# Quickstart: Layer 2 Tool `guideCategories_list`

## Goal

Verify that YT-223 exposes the low-level `guideCategories_list` tool as a deprecated, endpoint-backed Layer 2 lookup for YouTube guide categories.

## Prerequisites

- Work on branch `223-guidecategories-list`.
- Keep the YT-223 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for the contract, validation, result, error, export, and registration behavior.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `guideCategories_list`
   - upstream identity `guideCategories.list`
   - quota cost `1` in metadata, description, usage notes, and examples
   - auth mode `api_key`
   - availability state `deprecated`
   - required `part`
   - exactly one selector: `regionCode` or `id`
   - optional `hl` localization behavior
   - legacy unavailable outcome
2. Add failing unit tests for:
   - missing `part`
   - missing selector
   - conflicting selectors
   - invalid `regionCode`
   - invalid `id`
   - unsupported `hl`
   - unsupported channel, video-category, search, recommendation, ranking, summarization, enrichment, or taxonomy migration fields
   - guide category not found
   - empty successful results
   - deprecated endpoint and endpoint unavailable mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of a valid region lookup
   - dispatcher invocation of a valid ID lookup after the Layer 1 dependency supports it
   - safe error detail sanitization

## Green Phase

1. Add `src/mcp_server/tools/youtube_common/guide_categories.py`.
2. Define the smallest `guideCategories_list` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, and error mapper needed to pass the focused tests.
3. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Register the descriptor in the default tool catalog.
5. If ID lookup fails because Layer 1 only advertises `regionCode`, make the smallest Layer 1 wrapper metadata and validation update needed to support dependency-backed `id` lookup.
6. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep deprecated availability text visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, signed URLs, or secret-bearing fields.
4. Keep active `videoCategories`, channel, search, and higher-level taxonomy behavior out of the guide-categories module.

## Focused Verification

```bash
pytest tests/contract/test_youtube_guide_categories_contract.py tests/unit/test_youtube_guide_categories.py tests/integration/test_youtube_guide_categories_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `guideCategories_list` remains a deprecated, read-only guide-category lookup and does not provide channel listing, video-category lookup, search, ranking, summarization, enrichment, or taxonomy migration behavior.
- Local dispatcher validation may reject requests that miss both selectors before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Safe error detail sanitization strips API keys, OAuth tokens, raw request/body diagnostics, stack traces, and signed URL fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-223`
- focused test output for `guideCategories_list`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that the deprecated or unavailable platform behavior is visible in metadata, caveats, examples, and safe errors
