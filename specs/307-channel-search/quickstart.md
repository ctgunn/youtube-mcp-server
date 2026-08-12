# Quickstart: Verify `channels_searchChannels`

## Prerequisites

- Python 3.11 or later is available.
- Repository dependencies and the lint tool are installed.
- A configured runtime has public YouTube read capability when exercising a live integration path. Do not place secrets in commands, fixtures, logs, or documentation.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Verify Supporting Search-Contract Behavior

After implementation, run the focused lower-layer search suite:

```bash
python3 -m pytest \
  tests/unit/test_youtube_search.py \
  tests/contract/test_youtube_search_contract.py \
  tests/contract/test_layer1_search_contract.py \
  tests/integration/test_youtube_search_registration.py
```

This suite must prove that `channelType` is an additive supported optional field, permits only `any` and `show`, reaches the supported public search request path, and leaves existing callers unchanged when omitted.

## Verify the Public Contract and Behavior

Run the focused YT-307 suite:

```bash
python3 -m pytest \
  tests/unit/test_youtube_composed_channels.py \
  tests/contract/test_youtube_composed_channels_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py
```

The focused suite must demonstrate:

- query-only handle, name, and general channel search, including successful empty results;
- validation of every public parameter, time window, subscriber range, and unknown field;
- `channelType` and base-order application;
- conditional subscriber, latest-upload, and creator-only refinement;
- all five ranking modes with deterministic ties and final result bounds;
- safe partial-enrichment and lower-layer failure behavior;
- executable descriptor discovery and default dispatcher registration.

## Verify Protocol Error Safety

```bash
python3 -m pytest tests/unit/test_method_routing.py
```

This test must show that each YT-307 safe category serializes as an MCP-safe error with a stable public category and no unsafe diagnostics.

## Review Discovery Expectations

Confirm the discovered descriptor for `channels_searchChannels`:

- exposes the exact public input schema and no `representativeOnly` marker;
- identifies itself as bounded composed ranked enrichment;
- explains that subscriber/activity data is conditional public enrichment;
- identifies creator classification and `indie_priority` as heuristic;
- distinguishes source base-search continuation from final ranked-result pagination;
- documents quota, access, partial-result, and recovery behavior.

## Complete Repository Verification

After all feature changes and refactoring are complete, run:

```bash
python3 -m pytest
python3 -m ruff check .
```

Both commands must succeed before the feature is considered complete. The full suite is required even if all focused YT-307 checks pass.
