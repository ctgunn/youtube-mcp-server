# Quickstart: Verify `channels_findCreators`

## Prerequisites

- Python 3.11 or later is available.
- Repository dependencies and Ruff are installed.
- A configured runtime has public YouTube read capability when exercising a live integration path. Do not place secrets in commands, fixtures, logs, or documentation.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Verify the Public Contract and Behavior

After implementation, run the focused YT-308 suite:

```bash
python3 -m pytest \
  tests/unit/test_youtube_composed_channels.py \
  tests/contract/test_youtube_composed_channels_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py
```

The focused suite must demonstrate:

- query-only creator discovery from matching videos, successful empty results, and distinct-channel grouping;
- validation of every public parameter, date window, subscriber range, unknown field, and strict value type;
- a fixed bounded base video-candidate collection separate from the final channel cap;
- conditional subscriber, latest-upload, and creator-only refinement;
- all five ranking modes with deterministic ties and filtering before ranking;
- zero and positive per-channel sample limits, with samples in base-video order;
- safe partial-enrichment and lower-layer failure outcomes;
- executable descriptor discovery and default dispatcher registration.

## Verify Protocol Error Safety

```bash
python3 -m pytest tests/unit/test_method_routing.py
```

This test must show that each YT-308 safe category serializes as an MCP-safe error with a stable public category and no unsafe diagnostics.

## Review Discovery Expectations

Confirm the discovered descriptor for `channels_findCreators`:

- exposes the exact public input schema and no `representativeOnly` marker;
- identifies itself as a bounded composite ranked-enrichment workflow;
- documents video-derived candidate grouping, per-channel sample order and bounds, and base-only continuation;
- identifies subscriber/activity enrichment as conditional public enrichment;
- identifies creator classification and `indie_priority` as heuristic;
- documents quota, access, partial-result, and recovery behavior.

## Complete Repository Verification

After all feature changes and refactoring are complete, run:

```bash
python3 -m pytest
python3 -m ruff check .
```

Both commands must succeed before the feature is considered complete. The full suite is required even if all focused YT-308 checks pass.
