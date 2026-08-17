# Quickstart: Verify `channels_searchContent`

## Prerequisites

- Python 3.11 or later is available.
- Repository dependencies and the lint tool are installed.
- A configured runtime has public YouTube search capability when exercising a live integration path. Do not put secrets in commands, fixtures, logs, or documentation.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Review the Planned Contract

- `channels_searchContent` accepts exactly one trimmed nonblank `channelId`, one trimmed nonblank `query`, optional whole-number `maxResults` from 1 through 50 (default 10), optional `order` of `relevance`, `date`, or `viewCount` (default `relevance`), and an optional BCP 47 `language` relevance preference.
- Each invocation makes exactly one bounded public video search constrained to the requested channel. There is no caller-controlled continuation, channel/video hydration, transcript lookup, local enrichment, local filtering, or local ranking.
- Returned usable items retain direct-search source order after first-occurrence video de-duplication. Every returned item must identify the requested channel; malformed, duplicate, or mismatched source records are omitted and disclosed only in aggregate when applicable.
- A valid no-match search is a successful empty result with complete applied-input, search-context, and provenance data. A failed required search is a safe whole-request error, never a partial collection.
- A language preference refines relevance but does not guarantee returned content language. Public result fields preserve available source values; context, counts, and provenance are normalized.
- The feature adds no storage, source client, transport behavior, authentication flow, crawler, pagination traversal, or change to the Layer 2 `search_list` contract.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and routing tests for validation, exact one-search construction, direct-search semantics, source association, normalization, de-duplication, cap/order/language behavior, empty and safe failures, provenance, discovery metadata, and default registration.
2. **Green**: Add only the channels-family error, schema, validator, language helper, direct request mapper, candidate/result/metadata builders, handler, exports, and registration required by the failing tests.
3. **Refactor**: Consolidate local channels-family helpers, preserve direct-search behavior and safe error sanitization, add or preserve reStructuredText docstrings on every new or changed Python function, then rerun focused and full checks.

## Planned Verification Commands

Run focused checks during implementation:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/unit/test_youtube_composed_channels.py \
  tests/contract/test_youtube_composed_channels_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/unit/test_method_routing.py
```

Run these after the final code change:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

## Review Evidence

Pull-request review should include:

- The matched seed slice, `YT-318`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving `channels_searchContent` is concrete, default-registered, direct-search based, channel constrained, bounded, and has no representative-only marker.
- Result evidence for populated and empty searches; the default, minimum, and maximum `maxResults`; each supported order; valid and invalid language preferences; source association; source-order preservation; duplicate/malformed/out-of-scope omission; and full normalized response context.
- Safe-error evidence for invalid parameters, unavailable resource, authorization-sensitive data, capacity exhaustion, and source failure without unsafe details.
- Evidence that every invocation performs exactly one channel-constrained public video search and does not locally enrich, filter, or re-rank results.
- Passing full-suite and lint output.
- Confirmation that all new or changed Python functions have reStructuredText docstrings.
