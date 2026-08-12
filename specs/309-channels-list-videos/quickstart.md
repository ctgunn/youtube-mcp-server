# Quickstart: Verify `channels_listVideos`

## Prerequisites

- Python 3.11 or later is available.
- Repository dependencies and the lint tool are installed.
- A configured runtime has public YouTube read capability when exercising a live integration path. Do not place secrets in commands, fixtures, logs, or documentation.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Review the Planned Contract

- `channels_listVideos` accepts exactly one trimmed nonblank `channelId` and an optional whole-number `maxResults` from 1 through 50, defaulting to 10.
- The tool resolves the public uploads collection and makes at most one bounded collection listing; it does not use ranked search, query matching, pagination traversal, or item-detail enrichment.
- Results preserve usable source collection order at request time, de-duplicate by first video occurrence, then apply the result cap.
- A missing uploads collection or successful empty list is a successful empty response; a failed required read is a safe whole-request error.
- Every result identifies the uploads-collection source, public-content-only boundary, no-ranking behavior, and request-time variability through `collectionContext` and field provenance.
- A known unusable source item is omitted and disclosed only through safe aggregate `partialAvailability`; a failed required collection read is never presented as a partial result.
- Public video fields are source-preserved; counts, request context, and ordering context are normalized and labeled through provenance metadata.
- The feature adds no storage, source client, crawler, transport behavior, or change to lower-level contracts.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and protocol tests for validation, exact lower-layer calls, order, de-duplication, cap, empty and safe failure behavior, provenance, discovery metadata, and default registration.
2. **Green**: Add only the channel-family descriptor, validator, bounded two-read adapter, item mapper, safe error mapping, exports, and registration needed for those tests.
3. **Refactor**: Consolidate local channel-family helpers, retain reStructuredText docstrings on every new or changed Python function, then rerun focused and full checks.

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

- The matched seed slice, `YT-309`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving `channels_listVideos` is concrete, default-registered, source-ordered, bounded, and has no representative-only marker.
- Result evidence for a populated source collection, a successful empty collection, first-occurrence de-duplication, source-order preservation, default/minimum/maximum `maxResults`, and invalid request boundaries.
- Safe-result evidence for unavailable channel, authorization-sensitive, capacity, source-failure, and known item-level partial-availability cases, without unsafe details.
- Evidence that each invocation performs one channel lookup and at most one collection listing.
- Passing full-suite and lint output.
- Confirmation that all new or changed Python functions have reStructuredText docstrings.
