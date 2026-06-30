# Quickstart: Layer 2 Tool `i18nLanguages_list`

## Goal

Verify that YT-224 exposes the low-level `i18nLanguages_list` tool as an active, endpoint-backed Layer 2 lookup for YouTube localization-language reference data.

## Prerequisites

- Work on branch `224-i18n-languages-list`.
- Keep the YT-224 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for the contract, validation, result, error, export, and registration behavior.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `i18nLanguages_list`
   - upstream identity `i18nLanguages.list`
   - quota cost `1` in metadata, description, usage notes, and examples
   - auth mode `api_key`
   - availability state `active`
   - required `part`
   - supported `part=snippet`
   - optional `hl` display-language behavior
   - empty successful result behavior
2. Add failing unit tests for:
   - missing `part`
   - invalid `part`
   - unsupported `hl`
   - unsupported selectors, paging, region, caption-language, translation, language-detection, search, recommendation, ranking, summarization, enrichment, or aggregation fields
   - empty successful results
   - quota failure, upstream invalid request, endpoint unavailable, and unexpected upstream failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of a valid default lookup
   - dispatcher invocation of a valid display-language lookup
   - safe error detail sanitization
4. Add failing Layer 1 alignment coverage if the existing wrapper still requires `hl` for calls where the public Layer 2 request omits it.

## Green Phase

1. Add `src/mcp_server/tools/youtube_common/localization.py`.
2. Define the smallest `i18nLanguages_list` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, and error mapper needed to pass the focused tests.
3. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Register the descriptor in the default tool catalog.
5. If default lookup fails because Layer 1 requires `hl`, make the smallest Layer 1 wrapper metadata and validation update needed to support optional `hl` while preserving existing `part` plus `hl` calls.
6. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep localization-language usage text visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, signed URLs, or secret-bearing fields.
4. Keep translation, language detection, region lookup, caption-language availability, search, ranking, summarization, enrichment, and higher-level localization workflow behavior out of the localization-language tool.

## Focused Verification

```bash
pytest tests/contract/test_youtube_i18n_languages_contract.py tests/unit/test_youtube_i18n_languages.py tests/integration/test_youtube_i18n_languages_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `i18nLanguages_list` remains a read-only localization-language reference lookup and does not translate text, detect language, list regions, check caption language availability, search, rank, summarize, enrich, or aggregate data.
- Local dispatcher validation may reject unsupported fields before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Safe error detail sanitization strips API keys, OAuth tokens, raw request/body diagnostics, stack traces, and signed URL fields before errors are exposed to callers.
- The current Layer 1 wrapper may need a narrow alignment update because it was originally scoped to deterministic `part` plus `hl` calls, while the public Layer 2 endpoint contract supports omitted `hl`.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-224`
- focused test output for `i18nLanguages_list`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota, auth, active availability, required `part`, optional `hl`, empty-result behavior, and out-of-scope boundaries are visible in metadata, examples, and safe errors

Implementation evidence captured for this slice:

- Focused YT-224 verification: `python3 -m pytest tests/contract/test_youtube_i18n_languages_contract.py tests/unit/test_youtube_i18n_languages.py tests/integration/test_youtube_i18n_languages_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` passed with 161 tests.
- Layer 1 optional-`hl` contract alignment verification: `python3 -m pytest tests/contract/test_layer1_localization_contract.py tests/contract/test_layer1_metadata_contract.py` passed with 68 tests.
- Full repository verification: `python3 -m pytest` passed with 2425 tests.
- Lint verification: `python3 -m ruff check .` passed.
- New and changed Python functions were reviewed for reStructuredText docstrings.
- The implemented `i18nLanguages_list` scope remains limited to read-only localization-language lookup and excludes translation, language detection, region lookup, caption-language availability, search, ranking, summarization, enrichment, and aggregation.
